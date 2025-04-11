import os
from typing import Dict, List, Optional
import logging
from datetime import datetime
import openai
from ..models import db, Candidate, Job, Shortlist, Analytics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentFramework:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        openai.api_key = self.openai_api_key
        self.agents = {
            'resume_parser': self._create_resume_parser_agent(),
            'job_analyzer': self._create_job_analyzer_agent(),
            'match_maker': self._create_match_maker_agent(),
            'interview_scheduler': self._create_interview_scheduler_agent()
        }

    def _create_resume_parser_agent(self) -> Dict:
        return {
            'role': 'resume_parser',
            'system_prompt': """You are an expert resume parser. Extract the following information from resumes:
            1. Personal Information (name, email, phone)
            2. Skills and Technologies
            3. Work Experience
            4. Education
            5. Certifications
            6. Projects
            Format the output as structured JSON.""",
            'model': 'gpt-4'
        }

    def _create_job_analyzer_agent(self) -> Dict:
        return {
            'role': 'job_analyzer',
            'system_prompt': """You are an expert job description analyzer. Extract and categorize:
            1. Required Skills
            2. Experience Requirements
            3. Education Requirements
            4. Key Responsibilities
            5. Company Culture Indicators
            Format the output as structured JSON.""",
            'model': 'gpt-4'
        }

    def _create_match_maker_agent(self) -> Dict:
        return {
            'role': 'match_maker',
            'system_prompt': """You are an expert candidate-job matcher. Analyze and score matches based on:
            1. Skill Alignment
            2. Experience Match
            3. Education Fit
            4. Cultural Fit
            5. Growth Potential
            Provide a detailed match score and justification.""",
            'model': 'gpt-4'
        }

    def _create_interview_scheduler_agent(self) -> Dict:
        return {
            'role': 'interview_scheduler',
            'system_prompt': """You are an expert interview scheduler. Based on match scores and availability:
            1. Recommend interview rounds
            2. Suggest interviewers
            3. Propose timeline
            4. Prepare interview questions
            Format the output as structured JSON.""",
            'model': 'gpt-4'
        }

    async def process_resume(self, resume_text: str) -> Dict:
        """Process resume using resume parser agent."""
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.agents['resume_parser']['model'],
                messages=[
                    {"role": "system", "content": self.agents['resume_parser']['system_prompt']},
                    {"role": "user", "content": resume_text}
                ],
                temperature=0.3
            )
            return self._parse_agent_response(response)
        except Exception as e:
            logger.error(f"Error processing resume: {str(e)}")
            return None

    async def analyze_job(self, job_description: str) -> Dict:
        """Analyze job description using job analyzer agent."""
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.agents['job_analyzer']['model'],
                messages=[
                    {"role": "system", "content": self.agents['job_analyzer']['system_prompt']},
                    {"role": "user", "content": job_description}
                ],
                temperature=0.3
            )
            return self._parse_agent_response(response)
        except Exception as e:
            logger.error(f"Error analyzing job: {str(e)}")
            return None

    async def match_candidate(self, candidate_info: Dict, job_info: Dict) -> Dict:
        """Match candidate with job using match maker agent."""
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.agents['match_maker']['model'],
                messages=[
                    {"role": "system", "content": self.agents['match_maker']['system_prompt']},
                    {"role": "user", "content": f"Candidate: {candidate_info}\nJob: {job_info}"}
                ],
                temperature=0.3
            )
            return self._parse_agent_response(response)
        except Exception as e:
            logger.error(f"Error matching candidate: {str(e)}")
            return None

    async def schedule_interview(self, match_result: Dict) -> Dict:
        """Schedule interview using interview scheduler agent."""
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.agents['interview_scheduler']['model'],
                messages=[
                    {"role": "system", "content": self.agents['interview_scheduler']['system_prompt']},
                    {"role": "user", "content": str(match_result)}
                ],
                temperature=0.3
            )
            return self._parse_agent_response(response)
        except Exception as e:
            logger.error(f"Error scheduling interview: {str(e)}")
            return None

    def _parse_agent_response(self, response) -> Dict:
        """Parse agent response and extract structured data."""
        try:
            content = response.choices[0].message.content
            # Implement parsing logic based on your specific needs
            return eval(content) if isinstance(content, str) else content
        except Exception as e:
            logger.error(f"Error parsing agent response: {str(e)}")
            return None

    def get_match_score_color(self, score: float) -> str:
        """Get color code for match score."""
        if score >= 0.8:
            return 'success'  # Green
        elif score >= 0.6:
            return 'primary'  # Blue
        elif score >= 0.4:
            return 'warning'  # Yellow
        else:
            return 'danger'   # Red

    def extract_key_skills(self, candidate_info: Dict, job_info: Dict) -> Dict:
        """Extract and compare key skills between candidate and job."""
        try:
            candidate_skills = set(candidate_info.get('skills', []))
            job_skills = set(job_info.get('required_skills', []))
            
            matched_skills = list(candidate_skills.intersection(job_skills))
            missing_skills = list(job_skills - candidate_skills)
            additional_skills = list(candidate_skills - job_skills)
            
            return {
                'matched_skills': matched_skills,
                'missing_skills': missing_skills,
                'additional_skills': additional_skills,
                'match_percentage': len(matched_skills) / len(job_skills) if job_skills else 0
            }
        except Exception as e:
            logger.error(f"Error extracting key skills: {str(e)}")
            return None 