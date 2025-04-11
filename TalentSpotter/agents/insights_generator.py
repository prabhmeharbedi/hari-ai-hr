"""
InsightsGeneratorAgent for the AI Recruitment System.

This agent is responsible for generating insights about candidates
based on their profiles and match scores against job descriptions.
"""

import json
from typing import Dict, Any, List, Optional

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from agents.base_agent import BaseAgent
from utils.openai_integration import generate_candidate_insights


class InsightsGeneratorAgent(BaseAgent):
    """
    Agent that generates insights about candidates based on their profiles
    and match scores against job descriptions.
    """
    
    def __init__(self, model_name=None, provider=None):
        """
        Initialize the InsightsGeneratorAgent.
        
        Args:
            model_name: Name of the LLM model to use
            provider: Provider of the LLM ('ollama' or 'openai')
        """
        super().__init__(model_name, provider)
        
        self.prompt = PromptTemplate(
            input_variables=["candidate_data", "job_data", "match_data"],
            template="""
            You are a recruitment expert analyzing a candidate for a job position.
            
            JOB:
            {job_data}
            
            CANDIDATE:
            {candidate_data}
            
            MATCH SCORES:
            {match_data}
            
            Based on the above information, please generate the following insights about the candidate:
            1. Strengths: List the top 3-5 strengths of this candidate for this specific role
            2. Gaps: List any 2-4 skill or experience gaps that might be concerning
            3. Cultural Fit: A brief assessment of potential cultural fit based on their background
            4. Interview Questions: Suggest 3-5 specific questions to ask this candidate
            5. Development Areas: Suggest 2-3 areas for professional development if they're hired
            6. Hiring Recommendation: Provide a recommendation (Strongly Recommend, Recommend, Consider, Not Recommended)
            
            Format your response as a structured analysis for a hiring manager.
            """
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
        
    def generate_insights(
        self, 
        candidate_data: Dict[str, Any], 
        job_data: Dict[str, Any], 
        match_data: Dict[str, Any],
        use_openai: bool = True
    ) -> Dict[str, Any]:
        """
        Generate insights about a candidate based on their profile and match scores.
        
        Args:
            candidate_data: Dictionary containing candidate information
            job_data: Dictionary containing job description information
            match_data: Dictionary containing match score information
            use_openai: Whether to use OpenAI for enhanced insights (requires API key)
            
        Returns:
            Dictionary containing generated insights
        """
        # Try to use OpenAI for enhanced insights if requested
        if use_openai:
            try:
                return generate_candidate_insights(candidate_data, job_data, match_data)
            except Exception as e:
                print(f"Error using OpenAI for insights, falling back to Ollama: {e}")
                # Fall back to Ollama/LangChain
        
        # Format data for LangChain prompt
        formatted_candidate_data = json.dumps(candidate_data, indent=2)
        formatted_job_data = json.dumps(job_data, indent=2)
        formatted_match_data = json.dumps(match_data, indent=2)
        
        # Generate insights using LangChain
        result = self.chain.run(
            candidate_data=formatted_candidate_data,
            job_data=formatted_job_data,
            match_data=formatted_match_data
        )
        
        # Parse and structure the result
        # This is a simple parser that looks for specific sections in the text
        sections = [
            "Strengths:", "Gaps:", "Cultural Fit:", 
            "Interview Questions:", "Development Areas:", 
            "Hiring Recommendation:"
        ]
        
        insights = {}
        current_section = None
        current_content = []
        
        for line in result.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check if this line starts a new section
            is_section_start = False
            for section in sections:
                if line.startswith(section):
                    # Save current section if we have one
                    if current_section:
                        key = current_section.lower().replace(':', '').replace(' ', '_')
                        insights[key] = self._format_section_content(current_section, current_content)
                    
                    # Start new section
                    current_section = section.replace(':', '')
                    current_content = []
                    
                    # Get content after the section title
                    content = line[len(section):].strip()
                    if content:
                        current_content.append(content)
                        
                    is_section_start = True
                    break
                    
            if not is_section_start and current_section:
                current_content.append(line)
                
        # Save the last section
        if current_section:
            key = current_section.lower().replace(':', '').replace(' ', '_')
            insights[key] = self._format_section_content(current_section, current_content)
            
        return insights
        
    def _format_section_content(self, section: str, content: List[str]) -> Any:
        """
        Format the content of a section based on its type.
        
        Args:
            section: Section name
            content: List of content lines
            
        Returns:
            Formatted content (list, string, etc.)
        """
        # Join all content into a single string
        text = ' '.join(content)
        
        # Format based on section type
        if section in ["Strengths", "Gaps", "Interview Questions", "Development Areas"]:
            # Split list items (looking for numbered points or bullet points)
            items = []
            for line in content:
                # Remove common list markers
                clean_line = line.lstrip('- *•1234567890. ')
                if clean_line:
                    items.append(clean_line)
                    
            # If we didn't find list items, try to split by commas or semicolons
            if len(items) <= 1 and text:
                if ',' in text:
                    items = [item.strip() for item in text.split(',') if item.strip()]
                elif ';' in text:
                    items = [item.strip() for item in text.split(';') if item.strip()]
                    
            return items
        else:
            # Return as simple text for other sections
            return text.strip()
            
    def analyze_candidate_for_job(
        self, 
        candidate_id: int, 
        job_id: int,
        use_openai: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze a candidate for a specific job and generate insights.
        
        Args:
            candidate_id: ID of the candidate
            job_id: ID of the job
            use_openai: Whether to use OpenAI for enhanced insights
            
        Returns:
            Dictionary containing analysis and insights
        """
        from main import db
        from models import Candidate, JobDescription, MatchScore
        
        # Get candidate, job and match data
        candidate = Candidate.query.get(candidate_id)
        job = JobDescription.query.get(job_id)
        match = MatchScore.query.filter_by(
            candidate_id=candidate_id, 
            jd_id=job_id
        ).first()
        
        if not candidate or not job:
            return {"error": "Candidate or job not found"}
            
        if not match:
            return {"error": "No match data found for this candidate and job"}
            
        # Prepare data for insight generation
        candidate_data = {
            "name": candidate.name,
            "education": candidate.education_list(),
            "experience": candidate.experience_list(),
            "skills": candidate.skills_dict(),
            "certifications": candidate.certifications_list(),
            "cv_text": candidate.cv_text
        }
        
        job_data = {
            "job_title": job.job_title,
            "department": job.department,
            "required_experience": job.required_experience,
            "required_education": job.required_education,
            "required_skills": job.skills_dict(),
            "job_responsibilities": job.responsibilities_list()
        }
        
        match_data = {
            "overall_score": match.overall_score,
            "skills_score": match.skills_score,
            "experience_score": match.experience_score,
            "education_score": match.education_score,
            "certifications_score": match.certifications_score
        }
        
        # Generate insights
        insights = self.generate_insights(
            candidate_data, 
            job_data, 
            match_data,
            use_openai=use_openai
        )
        
        # Combine all data for the response
        return {
            "candidate": candidate_data,
            "job": job_data,
            "match": match_data,
            "insights": insights
        }
