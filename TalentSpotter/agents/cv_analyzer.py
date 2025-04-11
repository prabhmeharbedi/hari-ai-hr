"""
CV Analyzer Agent

This module contains the implementation of the CV Analyzer agent,
which extracts key information from candidate CVs.
"""

import logging
from typing import Dict, Any, Optional
from .base_agent import BaseAgent

# Configure logging
logger = logging.getLogger(__name__)

class CVAnalyzerAgent(BaseAgent):
    """Agent for analyzing candidate CVs."""
    
    def __init__(self, model_name: str = "phi-2", provider: str = "ollama"):
        """
        Initialize the CV Analyzer agent.
        
        Args:
            model_name: Name of the model to use
            provider: Provider of the LLM ('ollama' or 'openai')
        """
        super().__init__(model_name=model_name, provider=provider)
    
    def analyze_cv(self, cv_text: str) -> Dict[str, Any]:
        """
        Analyze a CV to extract key information.
        
        Args:
            cv_text: The full text of the CV
            
        Returns:
            Dictionary containing extracted candidate information
        """
        # Check if the models are available
        if not self._check_models():
            return {"error": True, "message": "LLM models not available"}
        
        try:
            # Create a system prompt for the CV analysis
            system_prompt = """
            You are an expert CV analyzer. Your task is to analyze 
            the given CV/resume and extract the following information:
            1. Name and contact details
            2. Skills (both technical and soft skills)
            3. Work experience (including company names, job titles, durations, and key accomplishments)
            4. Education (including degrees, institutions, and graduation years)
            5. Certifications and other qualifications
            
            Format your response as a JSON object with the following structure:
            {
                "name": "string",
                "contact": {
                    "email": "string",
                    "phone": "string"
                },
                "skills": {
                    "technical_skills": ["skill1", "skill2", ...],
                    "soft_skills": ["skill1", "skill2", ...]
                },
                "experience": [
                    {
                        "company": "string",
                        "title": "string",
                        "duration": "string",
                        "start_date": "string",
                        "end_date": "string",
                        "description": "string",
                        "achievements": ["achievement1", "achievement2", ...]
                    }
                ],
                "education": [
                    {
                        "degree": "string",
                        "institution": "string",
                        "year": "string",
                        "gpa": "string (if available)"
                    }
                ],
                "certifications": [
                    {
                        "name": "string",
                        "issuer": "string",
                        "date": "string"
                    }
                ]
            }
            """
            
            # Create a user prompt with the CV text
            user_prompt = f"""
            Please analyze the following CV/resume and extract the key information:
            
            {cv_text}
            
            Extract all relevant details for name, contact information, skills, work experience, 
            education, and certifications.
            """
            
            # Get the JSON response
            result = self.get_json_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.2  # Low temperature for more deterministic results
            )
            
            # Check for errors in JSON parsing
            if "error" in result:
                logger.error(f"Error analyzing CV: {result.get('message', 'Unknown error')}")
                return result
            
            # Validate the output to ensure it has the expected structure
            required_fields = ["name", "skills", "experience", "education"]
            for field in required_fields:
                if field not in result:
                    logger.warning(f"Incomplete analysis result - missing {field}")
                    return {
                        "error": True,
                        "message": f"Failed to extract complete information from CV (missing {field})",
                        "partial_result": result
                    }
            
            # Return the analysis result
            return {
                "analysis": result,
                "model": self.model_name
            }
            
        except Exception as e:
            logger.error(f"Error in analyze_cv: {str(e)}")
            return {
                "error": True,
                "message": f"Failed to analyze CV: {str(e)}"
            }