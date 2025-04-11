import os
import openai
from typing import List, Dict, Tuple
from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIMatchingService:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.matching_threshold = float(os.getenv('MATCHING_THRESHOLD', 0.7))
        self.max_candidates = int(os.getenv('MAX_CANDIDATES_PER_JOB', 10))
        openai.api_key = self.openai_api_key

    def extract_candidate_info(self, resume_text: str) -> Dict:
        """Extract candidate information from resume text using OpenAI."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Extract candidate information from the resume text."},
                    {"role": "user", "content": resume_text}
                ],
                temperature=0.3
            )
            return self._parse_candidate_info(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error extracting candidate info: {str(e)}")
            return None

    def calculate_match_score(self, job_description: str, candidate_info: Dict) -> float:
        """Calculate match score between job description and candidate info."""
        try:
            # Get embeddings for job description and candidate info
            job_embedding = self._get_embedding(job_description)
            candidate_embedding = self._get_embedding(str(candidate_info))
            
            # Calculate cosine similarity
            similarity = cosine_similarity([job_embedding], [candidate_embedding])[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating match score: {str(e)}")
            return 0.0

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI."""
        response = openai.Embedding.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response['data'][0]['embedding']

    def _parse_candidate_info(self, extracted_info: str) -> Dict:
        """Parse extracted candidate information into structured format."""
        # Implement parsing logic based on your specific needs
        return {
            "name": "",
            "email": "",
            "phone": "",
            "skills": [],
            "experience": 0,
            "education": [],
            "current_company": "",
            "current_position": ""
        }

    def process_candidates(self, job_id: int, candidates: List[Dict]) -> List[Dict]:
        """Process candidates and return those with high match scores."""
        processed_candidates = []
        
        for candidate in candidates:
            match_score = self.calculate_match_score(
                candidate['job_description'],
                candidate['info']
            )
            
            if match_score >= self.matching_threshold:
                processed_candidates.append({
                    **candidate,
                    'match_score': match_score,
                    'processed_at': datetime.utcnow(),
                    'status': 'shortlisted' if match_score >= 0.8 else 'review_needed'
                })
        
        # Sort by match score and limit to max candidates
        processed_candidates.sort(key=lambda x: x['match_score'], reverse=True)
        return processed_candidates[:self.max_candidates]

    def generate_interview_invitation(self, candidate: Dict, job: Dict) -> str:
        """Generate interview invitation email content."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Generate a professional interview invitation email."},
                    {"role": "user", "content": f"Candidate: {candidate}\nJob: {job}"}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating interview invitation: {str(e)}")
            return None 