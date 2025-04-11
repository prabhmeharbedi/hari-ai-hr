"""
Job Description Summarizer Agent

This module contains the implementation of the JD Summarizer agent,
which analyzes job descriptions to extract key requirements and responsibilities.
Uses Langchain for flexible model integration.
"""

import logging
from typing import Dict, Any, Optional
from .base_agent import BaseAgent

# Configure logging
logger = logging.getLogger(__name__)

class JDSummarizerAgent(BaseAgent):
    """Agent for analyzing and summarizing job descriptions using Langchain."""
    
    def __init__(self, model_name: str = "phi-2", provider: str = "ollama"):
        """
        Initialize the JD Summarizer agent.
        
        Args:
            model_name: Name of the model to use
            provider: Provider of the LLM ('ollama' or 'openai')
        """
        super().__init__(model_name=model_name, provider=provider)
    
    def analyze_job_description(self, job_description: str) -> Dict[str, Any]:
        """
        Analyze a job description to extract key information.
        
        Args:
            job_description: The full text of the job description
            
        Returns:
            Dictionary containing extracted job requirements and analysis
        """
        # Check if the models are available
        if not self._check_models():
            return {"error": True, "message": "LLM models not available"}
        
        try:
            # Define the output schema for structured parsing
            output_schema = {
                "job_title": {
                    "description": "The title of the job"
                },
                "skills": {
                    "description": "Dictionary containing technical_skills and soft_skills as lists"
                },
                "experience": {
                    "description": "Dictionary containing years (number) and details about required experience"
                },
                "education": {
                    "description": "Dictionary containing level and details about required education"
                },
                "responsibilities": {
                    "description": "List of job responsibilities"
                }
            }
            
            # Create a system prompt for the job description analysis
            system_prompt = """
            You are an expert job description analyzer. Your task is to analyze 
            the given job description and extract the following information:
            1. Job title
            2. Required skills (both technical and soft skills)
            3. Required experience (in years)
            4. Required education level
            5. Job responsibilities
            
            Be thorough and accurate in your extraction. If certain information
            is not explicitly provided, make reasonable inferences based on the
            context but indicate when you're making an inference.
            """
            
            # Create a user prompt with the job description
            user_prompt = f"""
            Please analyze the following job description and extract the key information:
            
            {job_description}
            
            Extract all relevant details for job title, skills (both technical and soft skills), required experience, 
            required education, and job responsibilities.
            """
            
            # Get the JSON response using the structured output schema
            result = self.get_json_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
                output_schema=output_schema,
                temperature=0.2  # Low temperature for more deterministic results
            )
            
            # Check for errors in JSON parsing
            if "error" in result:
                logger.error(f"Error analyzing job description: {result.get('message', 'Unknown error')}")
                return result
            
            # Validate the output to ensure it has the expected structure
            if "job_title" not in result or "skills" not in result:
                logger.warning("Incomplete analysis result - missing essential fields")
                return {
                    "error": True,
                    "message": "Failed to extract complete information from job description",
                    "partial_result": result
                }
            
            # Return the analysis result with model information
            return {
                "analysis": result,
                "model": self.model_name,
                "provider": self.provider
            }
            
        except Exception as e:
            logger.error(f"Error in analyze_job_description: {str(e)}")
            return {
                "error": True,
                "message": f"Failed to analyze job description: {str(e)}"
            }