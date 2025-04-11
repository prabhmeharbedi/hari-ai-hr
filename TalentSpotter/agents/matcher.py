"""
Candidate-Job Matching Agent

This module contains the implementation of the Matcher agent,
which evaluates how well a candidate matches a job description.
"""

import logging
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent

# Configure logging
logger = logging.getLogger(__name__)

class MatcherAgent(BaseAgent):
    """Agent for evaluating candidate-job matches."""
    
    def __init__(self, model_name: str = "phi-2", provider: str = "ollama"):
        """
        Initialize the Matcher agent.
        
        Args:
            model_name: Name of the model to use
            provider: Provider of the LLM ('ollama' or 'openai')
        """
        super().__init__(model_name=model_name, provider=provider)
    
    def evaluate_match(self, job_requirements: Dict[str, Any], candidate_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate how well a candidate matches a job description.
        
        Args:
            job_requirements: Dictionary containing job requirements
            candidate_profile: Dictionary containing candidate information
            
        Returns:
            Dictionary containing match scores and analysis
        """
        # Check if the models are available
        if not self._check_models():
            return {"error": True, "message": "LLM models not available"}
        
        try:
            # Create a system prompt for the matching evaluation
            system_prompt = """
            You are an expert recruitment matcher. Your task is to evaluate how well 
            a candidate matches a job description. Analyze the candidate's skills, 
            experience, education, and certifications against the job requirements.
            
            Provide numerical scores (0-100) for each category and an overall match score.
            For each category, also provide a brief explanation of the match strength.
            
            Format your response as a JSON object with the following structure:
            {
                "skills_match": {
                    "score": number (0-100),
                    "explanation": "string"
                },
                "experience_match": {
                    "score": number (0-100),
                    "explanation": "string"
                },
                "education_match": {
                    "score": number (0-100),
                    "explanation": "string"
                },
                "certification_match": {
                    "score": number (0-100),
                    "explanation": "string"
                },
                "overall_match": {
                    "score": number (0-100),
                    "explanation": "string",
                    "strengths": ["strength1", "strength2", ...],
                    "weaknesses": ["weakness1", "weakness2", ...]
                }
            }
            
            Be objective and thorough in your evaluation. The overall match should be a weighted 
            average with skills and experience weighing more heavily than education and certifications.
            """
            
            # Convert dictionaries to formatted strings for the prompt
            job_str = self._format_dict_to_string(job_requirements, "Job Requirements")
            candidate_str = self._format_dict_to_string(candidate_profile, "Candidate Profile")
            
            # Create a user prompt with the job and candidate information
            user_prompt = f"""
            Please evaluate how well the following candidate matches the job requirements:
            
            {job_str}
            
            {candidate_str}
            
            Evaluate the match in terms of skills, experience, education, and certifications.
            Provide a detailed analysis with numerical scores and explanations.
            """
            
            # Get the JSON response
            result = self.get_json_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3  # Slightly higher temperature to allow for more nuanced analysis
            )
            
            # Check for errors in JSON parsing
            if "error" in result:
                logger.error(f"Error evaluating match: {result.get('message', 'Unknown error')}")
                return result
            
            # Validate the output to ensure it has the expected structure
            required_fields = ["skills_match", "experience_match", "education_match", "overall_match"]
            for field in required_fields:
                if field not in result:
                    logger.warning(f"Incomplete match result - missing {field}")
                    return {
                        "error": True,
                        "message": f"Failed to complete matching evaluation (missing {field})",
                        "partial_result": result
                    }
            
            # Return the match result
            return result
            
        except Exception as e:
            logger.error(f"Error in evaluate_match: {str(e)}")
            return {
                "error": True,
                "message": f"Failed to evaluate match: {str(e)}"
            }
    
    def _format_dict_to_string(self, data: Dict[str, Any], title: str) -> str:
        """
        Format a dictionary into a readable string.
        
        Args:
            data: Dictionary to format
            title: Title for the formatted section
            
        Returns:
            Formatted string representation
        """
        result = [f"--- {title} ---"]
        
        for key, value in data.items():
            if isinstance(value, dict):
                result.append(f"{key.replace('_', ' ').title()}:")
                for sub_key, sub_value in value.items():
                    result.append(f"  - {sub_key.replace('_', ' ').title()}: {sub_value}")
            elif isinstance(value, list):
                result.append(f"{key.replace('_', ' ').title()}:")
                for item in value:
                    if isinstance(item, dict):
                        for sub_key, sub_value in item.items():
                            result.append(f"  - {sub_key.replace('_', ' ').title()}: {sub_value}")
                    else:
                        result.append(f"  - {item}")
            else:
                result.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(result)