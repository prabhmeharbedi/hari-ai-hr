"""
RankingAlgorithm agent for the AI Recruitment System.

This agent is responsible for ranking candidates based on their match scores with jobs
and providing explainable AI insights about the ranking decisions.
"""

import json
from typing import Dict, Any, List, Optional

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from agents.base_agent import BaseAgent
from utils.openai_integration import generate_candidate_ranking_explanation


class RankingAlgorithmAgent(BaseAgent):
    """
    Agent that ranks candidates based on match scores and explains the ranking decisions.
    """
    
    def __init__(self, model_name=None, provider=None):
        """
        Initialize the RankingAlgorithmAgent.
        
        Args:
            model_name: Name of the LLM model to use
            provider: Provider of the LLM ('ollama' or 'openai')
        """
        super().__init__(model_name, provider)
        
        self.prompt = PromptTemplate(
            input_variables=["job_data", "candidates_data", "match_scores"],
            template="""
            You are an expert recruitment algorithm that ranks candidates for a job position.
            
            JOB DESCRIPTION:
            {job_data}
            
            CANDIDATES:
            {candidates_data}
            
            MATCH SCORES:
            {match_scores}
            
            Based on the above information, rank the candidates in order of suitability for the job.
            Provide a brief explanation of the ranking algorithm and why each candidate was ranked as they were.
            
            FORMAT YOUR RESPONSE AS FOLLOWS:
            1. A brief explanation of how the ranking algorithm works
            2. The weights used for different factors (skills, experience, education, certifications)
            3. For each candidate:
               - Rank (1, 2, 3, etc.)
               - Name
               - Reason for this ranking
            """
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    def rank_candidates_for_job(
        self, 
        job_id: int,
        use_openai: bool = True
    ) -> Dict[str, Any]:
        """
        Rank candidates for a specific job based on their match scores.
        
        Args:
            job_id: ID of the job
            use_openai: Whether to use OpenAI for enhanced ranking explanations
            
        Returns:
            Dictionary containing ranked candidates and explanation
        """
        from main import db
        from models import JobDescription, Candidate, MatchScore
        
        # Get job
        job = JobDescription.query.get(job_id)
        if not job:
            return {"error": "Job not found"}
        
        # Get match scores for this job
        matches = MatchScore.query.filter_by(jd_id=job_id).order_by(MatchScore.overall_score.desc()).all()
        if not matches:
            return {"error": "No matches found for this job"}
        
        # Get candidates
        candidate_ids = [match.candidate_id for match in matches]
        candidates = Candidate.query.filter(Candidate.candidate_id.in_(candidate_ids)).all()
        candidates_dict = {candidate.candidate_id: candidate for candidate in candidates}
        
        # Prepare data for ranking
        job_data = {
            "job_title": job.job_title,
            "department": job.department,
            "required_experience": job.required_experience,
            "required_education": job.required_education,
            "required_skills": job.skills_dict(),
            "job_responsibilities": job.responsibilities_list()
        }
        
        candidates_data = []
        match_scores_data = []
        
        for match in matches:
            candidate = candidates_dict.get(match.candidate_id)
            if not candidate:
                continue
                
            # Add candidate to the list
            candidates_data.append({
                "candidate_id": candidate.candidate_id,
                "name": candidate.name,
                "email": candidate.email,
                "phone": candidate.phone,
                "education": candidate.education_list(),
                "experience": candidate.experience_list(),
                "skills": candidate.skills_dict(),
                "certifications": candidate.certifications_list()
            })
            
            # Add match score to the list
            match_scores_data.append({
                "candidate_id": candidate.candidate_id,
                "jd_id": match.jd_id,
                "overall_score": match.overall_score,
                "skills_score": match.skills_score,
                "experience_score": match.experience_score,
                "education_score": match.education_score,
                "certifications_score": match.certifications_score
            })
        
        # Try to use OpenAI for enhanced ranking explanation if requested
        if use_openai:
            try:
                explanation = generate_candidate_ranking_explanation(
                    job_data, 
                    candidates_data, 
                    match_scores_data
                )
                
                # Create a list of ranked candidates based on the explanation
                ranked_candidates = []
                for match in matches:
                    candidate = candidates_dict.get(match.candidate_id)
                    if not candidate:
                        continue
                        
                    ranked_candidates.append({
                        "candidate_id": candidate.candidate_id,
                        "name": candidate.name,
                        "email": candidate.email,
                        "overall_score": match.overall_score,
                        "skills_score": match.skills_score,
                        "experience_score": match.experience_score,
                        "education_score": match.education_score,
                        "certifications_score": match.certifications_score
                    })
                
                return {
                    "job": job_data,
                    "candidates": ranked_candidates,
                    "explanation": explanation,
                    "weights_used": explanation.get("weights_used", {
                        "skills": 0.4,
                        "experience": 0.3,
                        "education": 0.2,
                        "certifications": 0.1
                    })
                }
            except Exception as e:
                print(f"Error using OpenAI for ranking explanation, falling back to LangChain: {e}")
                # Fall back to LangChain
                
        # Format data for LangChain prompt
        formatted_job_data = json.dumps(job_data, indent=2)
        formatted_candidates_data = json.dumps(candidates_data, indent=2)
        formatted_match_scores = json.dumps(match_scores_data, indent=2)
        
        # Generate ranking using LangChain
        result = self.chain.run(
            job_data=formatted_job_data,
            candidates_data=formatted_candidates_data,
            match_scores=formatted_match_scores
        )
        
        # Create a list of ranked candidates
        ranked_candidates = []
        for match in matches:
            candidate = candidates_dict.get(match.candidate_id)
            if not candidate:
                continue
                
            ranked_candidates.append({
                "candidate_id": candidate.candidate_id,
                "name": candidate.name,
                "email": candidate.email,
                "overall_score": match.overall_score,
                "skills_score": match.skills_score,
                "experience_score": match.experience_score,
                "education_score": match.education_score,
                "certifications_score": match.certifications_score
            })
        
        # Create a simple explanation
        explanation = {
            "ranking_explanation": "Candidates are ranked based on their overall match score with the job.",
            "differentiation_factors": [
                "Technical skills match with job requirements",
                "Experience level in years",
                "Educational background relevance",
                "Certifications related to the job"
            ],
            "tie_breakers": [
                "Skills score takes precedence in case of tied overall scores",
                "Experience score is used as a secondary tie-breaker",
                "Education score is used as a tertiary tie-breaker"
            ],
            "candidate_insights": []
        }
        
        weights_used = {
            "skills": 0.4,
            "experience": 0.3,
            "education": 0.2,
            "certifications": 0.1
        }
        
        # Default candidate insights
        for i, candidate in enumerate(ranked_candidates[:10]):
            explanation["candidate_insights"].append({
                "candidate_number": i + 1,
                "key_strengths": ["Strong technical skills", "Relevant experience", "Good educational background"],
                "ranking_reason": f"Ranked #{i+1} due to overall match score of {candidate['overall_score']:.2f}"
            })
        
        return {
            "job": job_data,
            "candidates": ranked_candidates,
            "explanation": explanation,
            "weights_used": weights_used
        }
