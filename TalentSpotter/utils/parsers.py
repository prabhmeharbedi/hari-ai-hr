"""
Text parsing and extraction utilities
"""
import logging
import re
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class TextParser:
    """
    Utility class for parsing and extracting text from various sources
    """
    
    @staticmethod
    def extract_job_data_from_text(text: str) -> Dict[str, Any]:
        """
        Extract job description data from plain text
        
        Args:
            text: The raw job description text
            
        Returns:
            Dict containing extracted job data
        """
        # Initialize job data dictionary
        job_data = {
            'job_title': '',
            'department': '',
            'required_experience': 0,
            'required_education': '',
            'required_skills': {
                'technical_skills': [],
                'soft_skills': []
            },
            'certifications': [],
            'job_responsibilities': [],
            'company_info': ''
        }
        
        # Extract job title - look for common patterns at the beginning
        title_patterns = [
            r'^.*?position:?\s*(.*?)(?:\n|$)',
            r'^.*?job title:?\s*(.*?)(?:\n|$)',
            r'^.*?title:?\s*(.*?)(?:\n|$)',
            r'^.*?role:?\s*(.*?)(?:\n|$)',
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and match.group(1).strip():
                job_data['job_title'] = match.group(1).strip()
                break
                
        # Extract department
        dept_patterns = [
            r'department:?\s*(.*?)(?:\n|$)',
            r'team:?\s*(.*?)(?:\n|$)',
            r'division:?\s*(.*?)(?:\n|$)',
        ]
        
        for pattern in dept_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and match.group(1).strip():
                job_data['department'] = match.group(1).strip()
                break
                
        # Extract experience
        exp_patterns = [
            r'(\d+)(?:\+)?\s*(?:years|yrs)(?:\s*of)?(?:\s*experience)',
            r'experience:?\s*(\d+)(?:\+)?(?:\s*years|\s*yrs)',
            r'minimum(?:\s*of)?\s*(\d+)(?:\+)?(?:\s*years|\s*yrs)',
        ]
        
        for pattern in exp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and match.group(1).strip():
                try:
                    job_data['required_experience'] = int(match.group(1).strip())
                except ValueError:
                    pass
                break
                
        # Extract education
        edu_patterns = [
            r'education:?\s*(.*?)(?:\n|$)',
            r'degree:?\s*(.*?)(?:\n|$)',
            r'qualification:?\s*(.*?)(?:\n|$)',
        ]
        
        for pattern in edu_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match and match.group(1).strip():
                job_data['required_education'] = match.group(1).strip()
                break
        
        # Note: For more complex extractions like skills, responsibilities, etc.,
        # it's better to use ML/AI approaches rather than regex
        # The JD Summarizer Agent will handle these
        
        return job_data

    @staticmethod
    def extract_cv_data_from_text(text: str) -> Dict[str, Any]:
        """
        Extract candidate data from CV plain text
        
        Args:
            text: The raw CV text
            
        Returns:
            Dict containing extracted candidate data
        """
        # Initialize candidate data dictionary
        candidate_data = {
            'name': '',
            'contact_info': {
                'email': '',
                'phone': '',
                'location': ''
            },
            'education': [],
            'experience': [],
            'skills': {
                'technical': [],
                'soft': []
            },
            'certifications': [],
            'projects': []
        }
        
        # Extract name - usually one of the first lines
        name_pattern = r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
        match = re.search(name_pattern, text)
        if match and match.group(1).strip():
            candidate_data['name'] = match.group(1).strip()
            
        # Extract email
        email_pattern = r'\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b'
        email_match = re.search(email_pattern, text)
        if email_match and email_match.group(1).strip():
            candidate_data['contact_info']['email'] = email_match.group(1).strip()
            
        # Extract phone number
        phone_patterns = [
            r'\b(\+?\d{1,3}[- ]?\d{3}[- ]?\d{3}[- ]?\d{4})\b',
            r'\b(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})\b',
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match and match.group(1).strip():
                candidate_data['contact_info']['phone'] = match.group(1).strip()
                break
        
        # Note: For more complex extractions like education, experience, skills, etc.,
        # it's better to use ML/AI approaches rather than regex
        # The Recruiter Agent will handle these
        
        return candidate_data
        
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: The text to clean
            
        Returns:
            Cleaned text
        """
        # Replace multiple newlines with a single one
        text = re.sub(r'\n+', '\n', text)
        
        # Replace multiple spaces with a single one
        text = re.sub(r'\s+', ' ', text)
        
        # Remove non-printable characters
        text = re.sub(r'[^\x20-\x7E\n]', '', text)
        
        return text.strip()