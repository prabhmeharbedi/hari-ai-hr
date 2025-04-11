"""
Recruiter Agent for CV analysis and candidate-job matching
"""
import logging
from typing import Dict, Any, Optional

from agents.agent_utils import OllamaClient, AgentPrompts, extract_json_from_response

logger = logging.getLogger(__name__)

class RecruiterAgent:
    """
    Agent that extracts structured information from candidate CVs
    and calculates match scores against job requirements
    """
    
    def __init__(self, ollama_client: Optional[OllamaClient] = None):
        """Initialize the agent with an optional Ollama client"""
        self.ollama_client = ollama_client or OllamaClient()
        self.cv_model = "phi:2.7b"  # Default model for CV analysis
        self.matching_model = "phi:2.7b"  # Default model for matching
        logger.info(f"Initialized Recruiter Agent with CV model: {self.cv_model} and matching model: {self.matching_model}")
    
    async def extract_cv_data(self, cv_text: str) -> Dict[str, Any]:
        """
        Extract structured data from a candidate's CV
        
        Args:
            cv_text: The raw text extracted from a CV
            
        Returns:
            Dict containing structured information from the CV
        """
        try:
            # Format the prompt
            prompt = AgentPrompts.RECRUITER_PROMPT.format(
                cv_text=cv_text
            )
            
            # Get response from the model
            response = await self.ollama_client.generate(
                model=self.cv_model,
                prompt=prompt,
                system=AgentPrompts.RECRUITER_SYSTEM,
                temperature=0.3  # Lower temperature for more consistent extraction
            )
            
            # Check for errors
            if "error" in response:
                logger.error(f"Error from Ollama API: {response['error']}")
                return self._create_default_cv_response()
            
            # Extract JSON from the response
            if "response" in response:
                extracted_data = extract_json_from_response(response["response"])
                
                # Validate and fix extracted data
                if not extracted_data:
                    logger.warning("Failed to extract JSON from response")
                    return self._create_default_cv_response()
                
                # Ensure required fields are present
                if "skills" not in extracted_data:
                    extracted_data["skills"] = {
                        "technical": [],
                        "soft": []
                    }
                
                if "education" not in extracted_data:
                    extracted_data["education"] = []
                
                if "experience" not in extracted_data:
                    extracted_data["experience"] = []
                
                return extracted_data
            
            logger.warning("Unexpected response format from Ollama API")
            return self._create_default_cv_response()
        
        except Exception as e:
            logger.error(f"Error extracting CV data: {e}")
            return self._create_default_cv_response()
    
    async def calculate_match_score(self, job_data: Dict[str, Any], candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate match scores between a job and a candidate
        
        Args:
            job_data: Structured job description data
            candidate_data: Structured candidate data
            
        Returns:
            Dict containing match scores and details
        """
        try:
            # Format job requirements and candidate profile for the prompt
            job_requirements = self._format_job_requirements(job_data)
            candidate_profile = self._format_candidate_profile(candidate_data)
            
            # Format the prompt
            prompt = AgentPrompts.MATCHING_PROMPT.format(
                job_requirements=job_requirements,
                candidate_profile=candidate_profile
            )
            
            # Get response from the model
            response = await self.ollama_client.generate(
                model=self.matching_model,
                prompt=prompt,
                system=AgentPrompts.MATCHING_SYSTEM,
                temperature=0.3  # Lower temperature for more consistent evaluation
            )
            
            # Check for errors
            if "error" in response:
                logger.error(f"Error from Ollama API: {response['error']}")
                return self._create_default_match_response()
            
            # Extract JSON from the response
            if "response" in response:
                extracted_data = extract_json_from_response(response["response"])
                
                # Validate and fix extracted data
                if not extracted_data:
                    logger.warning("Failed to extract JSON from response")
                    return self._create_default_match_response()
                
                # Ensure all required score components are present
                required_scores = ["skills_match", "experience_match", "education_match", "certification_match", "overall_match"]
                for score in required_scores:
                    if score not in extracted_data:
                        extracted_data[score] = {
                            "score": 0,
                            "details": "Not evaluated" if score != "overall_match" else "Summary not available"
                        }
                
                # Convert score values to float
                for score_type in required_scores:
                    if "score" in extracted_data[score_type]:
                        try:
                            extracted_data[score_type]["score"] = float(extracted_data[score_type]["score"])
                        except (ValueError, TypeError):
                            extracted_data[score_type]["score"] = 0
                
                return extracted_data
            
            logger.warning("Unexpected response format from Ollama API")
            return self._create_default_match_response()
        
        except Exception as e:
            logger.error(f"Error calculating match score: {e}")
            return self._create_default_match_response()
    
    def _format_job_requirements(self, job_data: Dict[str, Any]) -> str:
        """Format job requirements as a string for the prompt"""
        # Start with job title and department
        formatted = f"Job Title: {job_data.get('job_title', 'Not specified')}\n"
        if "department" in job_data and job_data["department"]:
            formatted += f"Department: {job_data['department']}\n"
        
        # Add experience requirements
        formatted += f"Required Experience: {job_data.get('required_experience', 0)} years\n"
        
        # Add education requirements
        formatted += f"Required Education: {job_data.get('required_education', 'Not specified')}\n"
        
        # Add skills
        formatted += "Required Skills:\n"
        if "required_skills" in job_data and isinstance(job_data["required_skills"], dict):
            # Technical skills
            formatted += "- Technical Skills:\n"
            tech_skills = job_data["required_skills"].get("technical_skills", [])
            if isinstance(tech_skills, list) and tech_skills:
                for skill in tech_skills:
                    formatted += f"  * {skill}\n"
            else:
                formatted += "  * None specified\n"
            
            # Soft skills
            formatted += "- Soft Skills:\n"
            soft_skills = job_data["required_skills"].get("soft_skills", [])
            if isinstance(soft_skills, list) and soft_skills:
                for skill in soft_skills:
                    formatted += f"  * {skill}\n"
            else:
                formatted += "  * None specified\n"
        else:
            formatted += "- Not specified\n"
        
        # Add certifications
        formatted += "Required Certifications:\n"
        certifications = job_data.get("certifications", [])
        if isinstance(certifications, list) and certifications:
            for cert in certifications:
                formatted += f"- {cert}\n"
        else:
            formatted += "- None specified\n"
        
        # Add responsibilities
        formatted += "Job Responsibilities:\n"
        responsibilities = job_data.get("job_responsibilities", [])
        if isinstance(responsibilities, list) and responsibilities:
            for resp in responsibilities:
                formatted += f"- {resp}\n"
        elif isinstance(responsibilities, str) and responsibilities:
            formatted += f"{responsibilities}\n"
        else:
            formatted += "- Not specified\n"
        
        return formatted
    
    def _format_candidate_profile(self, candidate_data: Dict[str, Any]) -> str:
        """Format candidate profile as a string for the prompt"""
        # Start with name and contact info
        formatted = f"Candidate: {candidate_data.get('name', 'Not specified')}\n"
        
        if "contact_info" in candidate_data and isinstance(candidate_data["contact_info"], dict):
            contact = candidate_data["contact_info"]
            if "email" in contact and contact["email"]:
                formatted += f"Email: {contact['email']}\n"
            if "phone" in contact and contact["phone"]:
                formatted += f"Phone: {contact['phone']}\n"
            if "location" in contact and contact["location"]:
                formatted += f"Location: {contact['location']}\n"
        
        # Add education
        formatted += "Education:\n"
        education = candidate_data.get("education", [])
        if isinstance(education, list) and education:
            for edu in education:
                if isinstance(edu, dict):
                    degree = edu.get("degree", "Degree not specified")
                    institution = edu.get("institution", "Institution not specified")
                    year = edu.get("year", "Year not specified")
                    formatted += f"- {degree} from {institution}, {year}\n"
                else:
                    formatted += f"- {edu}\n"
        else:
            formatted += "- Not specified\n"
        
        # Add experience
        formatted += "Work Experience:\n"
        experience = candidate_data.get("experience", [])
        if isinstance(experience, list) and experience:
            for exp in experience:
                if isinstance(exp, dict):
                    title = exp.get("title", "Title not specified")
                    company = exp.get("company", "Company not specified")
                    duration = exp.get("duration", "Duration not specified")
                    description = exp.get("description", "")
                    formatted += f"- {title} at {company}, {duration}\n"
                    if description:
                        formatted += f"  Description: {description}\n"
                else:
                    formatted += f"- {exp}\n"
        else:
            formatted += "- Not specified\n"
        
        # Add skills
        formatted += "Skills:\n"
        if "skills" in candidate_data and isinstance(candidate_data["skills"], dict):
            # Technical skills
            formatted += "- Technical Skills:\n"
            tech_skills = candidate_data["skills"].get("technical", [])
            if isinstance(tech_skills, list) and tech_skills:
                for skill in tech_skills:
                    formatted += f"  * {skill}\n"
            else:
                formatted += "  * None specified\n"
            
            # Soft skills
            formatted += "- Soft Skills:\n"
            soft_skills = candidate_data["skills"].get("soft", [])
            if isinstance(soft_skills, list) and soft_skills:
                for skill in soft_skills:
                    formatted += f"  * {skill}\n"
            else:
                formatted += "  * None specified\n"
        else:
            formatted += "- Not specified\n"
        
        # Add certifications
        formatted += "Certifications:\n"
        certifications = candidate_data.get("certifications", [])
        if isinstance(certifications, list) and certifications:
            for cert in certifications:
                formatted += f"- {cert}\n"
        else:
            formatted += "- None specified\n"
        
        # Add projects
        formatted += "Projects:\n"
        projects = candidate_data.get("projects", [])
        if isinstance(projects, list) and projects:
            for project in projects:
                formatted += f"- {project}\n"
        else:
            formatted += "- None specified\n"
        
        return formatted
    
    def _create_default_cv_response(self) -> Dict[str, Any]:
        """Create a default response for CV extraction errors"""
        return {
            "name": "Unknown",
            "contact_info": {
                "email": "",
                "phone": "",
                "location": ""
            },
            "education": [],
            "experience": [],
            "skills": {
                "technical": [],
                "soft": []
            },
            "certifications": [],
            "projects": []
        }
    
    def _create_default_match_response(self) -> Dict[str, Any]:
        """Create a default response for matching errors"""
        return {
            "skills_match": {
                "score": 0,
                "details": "Unable to evaluate skills match"
            },
            "experience_match": {
                "score": 0,
                "details": "Unable to evaluate experience match"
            },
            "education_match": {
                "score": 0,
                "details": "Unable to evaluate education match"
            },
            "certification_match": {
                "score": 0,
                "details": "Unable to evaluate certification match"
            },
            "overall_match": {
                "score": 0,
                "summary": "Unable to evaluate overall match"
            }
        }
    
    def set_models(self, cv_model: str, matching_model: str) -> None:
        """Set the models to use for CV analysis and matching"""
        self.cv_model = cv_model
        self.matching_model = matching_model
        logger.info(f"Set Recruiter models to: CV={cv_model}, Matching={matching_model}")

# Test function for the agent
async def test_agent():
    """Test the Recruiter Agent with a sample CV and job data"""
    # Sample CV text
    sample_cv = """
    John Smith
    Email: john.smith@example.com
    Phone: (555) 123-4567
    Location: San Francisco, CA
    
    Education:
    Master of Science in Computer Science, Stanford University, 2018
    Bachelor of Science in Computer Engineering, MIT, 2016
    
    Work Experience:
    Senior Machine Learning Engineer, Tech Solutions Inc. (2018-Present)
    - Developed and deployed machine learning models for computer vision applications
    - Implemented end-to-end ML pipeline using TensorFlow and PyTorch
    - Collaborated with cross-functional teams to integrate ML solutions into products
    
    Machine Learning Intern, AI Research Lab (Summer 2017)
    - Researched state-of-the-art deep learning techniques for NLP
    - Implemented several neural network architectures for sentiment analysis
    
    Skills:
    - Programming Languages: Python, C++, Java
    - ML Frameworks: TensorFlow, PyTorch, Scikit-learn
    - Cloud Platforms: AWS, GCP
    - Tools: Docker, Kubernetes, Git
    - Soft Skills: Communication, teamwork, problem-solving
    
    Certifications:
    - AWS Certified Machine Learning Specialty
    - Google Cloud Professional Machine Learning Engineer
    
    Projects:
    - Real-time Object Detection System using YOLOv5
    - Sentiment Analysis API for Social Media Data
    - Distributed Training Pipeline for Large Language Models
    """
    
    # Sample job data
    sample_job = {
        "job_title": "Senior AI Engineer",
        "department": "AI Research",
        "required_experience": 5,
        "required_education": "Master's or PhD in Computer Science, AI, or related field",
        "required_skills": {
            "technical_skills": [
                "Python",
                "TensorFlow or PyTorch",
                "Machine Learning",
                "Computer Vision",
                "Cloud Platforms (AWS/GCP)"
            ],
            "soft_skills": [
                "Communication",
                "Teamwork",
                "Problem-solving"
            ]
        },
        "certifications": [
            "Cloud ML certifications preferred"
        ],
        "job_responsibilities": [
            "Design and implement machine learning models",
            "Optimize model performance and scalability",
            "Collaborate with product teams to integrate AI solutions",
            "Stay up-to-date with latest research and technologies"
        ],
        "company_info": "Leading AI research company focused on computer vision applications"
    }
    
    # Create agent and test both functions
    agent = RecruiterAgent()
    
    # Extract CV data
    cv_data = await agent.extract_cv_data(sample_cv)
    print("CV Data:")
    print(cv_data)
    print("\n" + "-"*50 + "\n")
    
    # Calculate match score
    match_score = await agent.calculate_match_score(sample_job, cv_data)
    print("Match Score:")
    print(match_score)

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_agent())