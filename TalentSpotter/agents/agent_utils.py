"""
Utility functions for AI agents
"""
import os
import json
import logging
import re
from typing import Dict, List, Any, Optional, Union
import httpx
import asyncio

logger = logging.getLogger(__name__)

# Default config for Ollama API
OLLAMA_API_BASE = os.environ.get('OLLAMA_API_BASE', 'http://localhost:11434')
OLLAMA_TIMEOUT = int(os.environ.get('OLLAMA_TIMEOUT', '30'))

class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, api_base: str = OLLAMA_API_BASE, timeout: int = OLLAMA_TIMEOUT):
        """
        Initialize the Ollama client
        
        Args:
            api_base: Base URL for the Ollama API
            timeout: Timeout in seconds for API requests
        """
        self.api_base = api_base
        self.timeout = timeout
        logger.info(f"Initialized Ollama client with API base: {api_base}")
    
    async def generate(self, 
                 model: str, 
                 prompt: str, 
                 system: Optional[str] = None, 
                 temperature: float = 0.7, 
                 max_tokens: int = 2048) -> Dict[str, Any]:
        """
        Generate a completion using Ollama API
        
        Args:
            model: The name of the model to use
            prompt: The prompt to send to the model
            system: Optional system prompt
            temperature: Sampling temperature (higher = more creative)
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Dict containing the response from the API
        """
        try:
            url = f"{self.api_base}/api/generate"
            
            # Prepare request payload
            payload = {
                "model": model,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            if system:
                payload["system"] = system
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error generating with Ollama: {e}")
            return {
                "error": str(e),
                "response": "I encountered an error while generating a response. Please check the logs."
            }
    
    async def chat(self, 
              model: str, 
              messages: List[Dict[str, str]], 
              temperature: float = 0.7,
              max_tokens: int = 2048) -> Dict[str, Any]:
        """
        Generate a chat completion using Ollama API
        
        Args:
            model: The name of the model to use
            messages: List of message objects with role and content
            temperature: Sampling temperature (higher = more creative)
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            Dict containing the response from the API
        """
        try:
            url = f"{self.api_base}/api/chat"
            
            # Prepare request payload
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error chatting with Ollama: {e}")
            return {
                "error": str(e),
                "response": "I encountered an error while generating a chat response. Please check the logs."
            }
    
    async def embeddings(self, model: str, text: Union[str, List[str]]) -> Dict[str, Any]:
        """
        Generate embeddings using Ollama API
        
        Args:
            model: The name of the model to use
            text: Text or list of texts to generate embeddings for
            
        Returns:
            Dict containing the embeddings
        """
        try:
            url = f"{self.api_base}/api/embeddings"
            
            # Prepare request payload
            payload = {
                "model": model,
                "prompt": text if isinstance(text, str) else "\n".join(text)
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error generating embeddings with Ollama: {e}")
            return {
                "error": str(e),
                "embedding": []
            }

class AgentPrompts:
    """Collection of prompts for different agents"""
    
    JD_SUMMARIZER_SYSTEM = """
    You are a Job Description Analysis Expert. Your task is to analyze job descriptions and extract key information in a structured format.
    Focus on identifying:
    1. Job title and level
    2. Required technical skills
    3. Required soft skills
    4. Years of experience needed
    5. Educational qualifications
    6. Certifications required
    7. Key job responsibilities
    8. Company information

    Always output the information in a structured JSON format.
    """
    
    JD_SUMMARIZER_PROMPT = """
    Please analyze the following job description and extract the key information.
    
    JOB DESCRIPTION:
    {job_description}
    
    Return the extracted information in the following JSON format:
    {{
        "job_title": "The title of the job",
        "department": "The department or team this role belongs to (if mentioned)",
        "required_experience": "The number of years of experience required (integer)",
        "required_education": "The required educational qualifications",
        "required_skills": {{
            "technical_skills": ["skill1", "skill2", ...],
            "soft_skills": ["skill1", "skill2", ...]
        }},
        "certifications": ["certification1", "certification2", ...],
        "job_responsibilities": ["responsibility1", "responsibility2", ...],
        "company_info": "Brief information about the company"
    }}
    
    Ensure all fields are filled based on information in the job description. If some information is not explicitly mentioned, use "Not specified" or an empty array [].
    """
    
    RECRUITER_SYSTEM = """
    You are a CV Analysis Expert. Your task is to extract relevant information from candidate CVs and structure it for further processing.
    Focus on identifying:
    1. Name and contact information
    2. Education history
    3. Work experience (including years and roles)
    4. Technical skills
    5. Soft skills
    6. Certifications
    7. Projects and achievements

    Always output the information in a structured JSON format.
    """
    
    RECRUITER_PROMPT = """
    Please analyze the following CV and extract the key information.
    
    CV TEXT:
    {cv_text}
    
    Return the extracted information in the following JSON format:
    {{
        "name": "Candidate's full name",
        "contact_info": {{
            "email": "email address",
            "phone": "phone number",
            "location": "location (if mentioned)"
        }},
        "education": [
            {{
                "degree": "degree name",
                "institution": "university/college name",
                "year": "graduation year"
            }}
        ],
        "experience": [
            {{
                "title": "job title",
                "company": "company name",
                "duration": "duration in years",
                "description": "brief description of responsibilities"
            }}
        ],
        "skills": {{
            "technical": ["skill1", "skill2", ...],
            "soft": ["skill1", "skill2", ...]
        }},
        "certifications": ["certification1", "certification2", ...],
        "projects": ["project1", "project2", ...]
    }}
    
    Ensure all fields are filled based on information in the CV. If some information is not explicitly mentioned, use "Not specified" or an empty array [].
    """
    
    MATCHING_SYSTEM = """
    You are a Candidate-Job Matching Expert. Your task is to evaluate how well a candidate's profile matches a specific job description.
    Consider the following factors:
    1. Skills match (both technical and soft skills)
    2. Experience relevance and duration
    3. Education alignment
    4. Certification alignment

    Provide a detailed analysis and numerical scores for each category.
    """
    
    MATCHING_PROMPT = """
    Please evaluate how well the candidate matches the job requirements.
    
    JOB REQUIREMENTS:
    {job_requirements}
    
    CANDIDATE PROFILE:
    {candidate_profile}
    
    Return the match analysis in the following JSON format:
    {{
        "skills_match": {{
            "score": A number between 0 and 100,
            "details": "Explanation of the skills match evaluation"
        }},
        "experience_match": {{
            "score": A number between 0 and 100,
            "details": "Explanation of the experience match evaluation"
        }},
        "education_match": {{
            "score": A number between 0 and 100,
            "details": "Explanation of the education match evaluation"
        }},
        "certification_match": {{
            "score": A number between 0 and 100,
            "details": "Explanation of the certification match evaluation"
        }},
        "overall_match": {{
            "score": A weighted average of the above scores,
            "summary": "Brief summary of overall match"
        }}
    }}
    
    Base your evaluation on how well the candidate's profile meets the specific requirements of the job.
    """
    
    SHORTLISTING_SYSTEM = """
    You are a Candidate Shortlisting Expert. Your task is to evaluate candidates based on their match scores and determine if they should be shortlisted.
    Consider:
    1. Overall match score
    2. Specific match scores in critical areas
    3. Any specific requirements that are "must-haves"

    Provide a clear shortlisting decision with justification.
    """
    
    SHORTLISTING_PROMPT = """
    Please evaluate whether the following candidate should be shortlisted for the job.
    
    JOB DESCRIPTION:
    {job_description}
    
    CANDIDATE MATCH SCORES:
    {match_scores}
    
    THRESHOLD FOR SHORTLISTING: {threshold}
    
    Return your analysis in the following JSON format:
    {{
        "shortlist_decision": true or false,
        "confidence": A number between 0 and 100 indicating confidence in this decision,
        "justification": "Explanation of your decision",
        "suggested_interview_topics": ["topic1", "topic2", ...] (if shortlisted)
    }}
    
    Make your decision based on the match scores and whether the candidate meets the critical requirements for the job.
    """
    
    SCHEDULER_SYSTEM = """
    You are an Interview Email Generator. Your task is to create personalized, professional email templates for interview invitations.
    The emails should:
    1. Be professional and friendly
    2. Include all necessary interview details
    3. Be personalized to the candidate and position
    4. Include clear next steps

    Create email content that is engaging and represents the company well.
    """
    
    SCHEDULER_PROMPT = """
    Please generate an interview invitation email for the following scenario:
    
    JOB TITLE: {job_title}
    COMPANY: {company_name}
    CANDIDATE NAME: {candidate_name}
    INTERVIEW FORMAT: {interview_format}
    INTERVIEW DATE OPTIONS: {date_options}
    INTERVIEW DURATION: {duration}
    SPECIAL INSTRUCTIONS: {special_instructions}
    
    Create a complete, ready-to-send email including:
    - Subject line
    - Greeting
    - Introduction
    - Interview details
    - Preparation instructions
    - Next steps
    - Sign-off

    The tone should be professional but friendly, and the email should be personalized to both the candidate and the position.
    """

def extract_json_from_response(response_text):
    """Extract JSON from a text response that might contain additional text"""
    # Try to find JSON content using regex pattern matching
    json_pattern = r'(\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\})'
    json_matches = re.findall(json_pattern, response_text)
    
    if json_matches:
        # Start with the largest match as it's likely the complete JSON
        json_matches.sort(key=len, reverse=True)
        
        for json_str in json_matches:
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                continue
    
    # If regex failed, try looking for content between triple backticks (markdown code blocks)
    code_block_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
    code_blocks = re.findall(code_block_pattern, response_text)
    
    if code_blocks:
        for block in code_blocks:
            try:
                return json.loads(block)
            except json.JSONDecodeError:
                continue
    
    # If all else fails, treat the entire response as JSON
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        logger.error(f"Failed to extract JSON from response: {response_text[:100]}...")
        return {}