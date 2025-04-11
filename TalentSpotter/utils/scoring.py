import logging
import re
from typing import Dict, Any, List, Set, Tuple
import json
from difflib import SequenceMatcher

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MatchScorer:
    """
    Utility class for calculating match scores between job requirements
    and candidate profiles
    """
    
    @staticmethod
    def calculate_skills_score(job_skills: Dict[str, List[str]], 
                             candidate_skills: Dict[str, List[str]]) -> Tuple[float, str]:
        """
        Calculate a skill match score
        
        Args:
            job_skills: Dict with 'technical_skills' and 'soft_skills' lists
            candidate_skills: Dict with 'technical' and 'soft' skills lists
            
        Returns:
            Tuple of (score, details)
        """
        try:
            # Normalize skill lists
            job_technical = [s.lower() for s in job_skills.get('technical_skills', [])]
            job_soft = [s.lower() for s in job_skills.get('soft_skills', [])]
            
            candidate_technical = [s.lower() for s in candidate_skills.get('technical', [])]
            candidate_soft = [s.lower() for s in candidate_skills.get('soft', [])]
            
            # Handle empty skills lists
            if not job_technical and not job_soft:
                return 100.0, "No skills requirements specified"
            
            # Calculate technical skills match
            tech_score, tech_matches, tech_missing = MatchScorer._calculate_skill_set_match(
                job_technical, candidate_technical)
            
            # Calculate soft skills match
            soft_score, soft_matches, soft_missing = MatchScorer._calculate_skill_set_match(
                job_soft, candidate_soft)
            
            # Weight technical skills more heavily (70% technical, 30% soft)
            if job_technical and job_soft:
                final_score = (tech_score * 0.7) + (soft_score * 0.3)
            elif job_technical:
                final_score = tech_score
            else:
                final_score = soft_score
            
            # Prepare detailed explanation
            details = []
            
            if tech_matches:
                details.append(f"Matched technical skills: {', '.join(tech_matches)}")
            if tech_missing:
                details.append(f"Missing technical skills: {', '.join(tech_missing)}")
            if soft_matches:
                details.append(f"Matched soft skills: {', '.join(soft_matches)}")
            if soft_missing:
                details.append(f"Missing soft skills: {', '.join(soft_missing)}")
                
            detail_text = "\n".join(details)
            
            return final_score, detail_text
            
        except Exception as e:
            logger.error(f"Error calculating skills score: {e}")
            return 0.0, f"Error in calculation: {str(e)}"
    
    @staticmethod
    def _calculate_skill_set_match(job_skills: List[str], 
                                candidate_skills: List[str]) -> Tuple[float, List[str], List[str]]:
        """
        Calculate match for a set of skills
        
        Args:
            job_skills: List of required skills
            candidate_skills: List of candidate skills
            
        Returns:
            Tuple of (score, matched skills, missing skills)
        """
        if not job_skills:
            return 100.0, [], []
        
        matched_skills = []
        similar_skills = []
        missing_skills = []
        
        for job_skill in job_skills:
            # Check for exact match
            if job_skill in candidate_skills:
                matched_skills.append(job_skill)
                continue
            
            # Check for similar skills (e.g., "React" vs "ReactJS")
            found_similar = False
            for candidate_skill in candidate_skills:
                similarity = SequenceMatcher(None, job_skill, candidate_skill).ratio()
                
                # Also check if one is subset of another
                subset_match = job_skill in candidate_skill or candidate_skill in job_skill
                
                if similarity > 0.8 or subset_match:
                    similar_skills.append(f"{job_skill} ≈ {candidate_skill}")
                    found_similar = True
                    break
            
            if not found_similar:
                missing_skills.append(job_skill)
        
        # Calculate score
        if not job_skills:
            score = 100.0
        else:
            # Weight exact matches higher than similar matches
            match_count = len(matched_skills) + (len(similar_skills) * 0.8)
            score = (match_count / len(job_skills)) * 100
        
        return score, matched_skills + similar_skills, missing_skills
    
    @staticmethod
    def calculate_experience_score(job_experience: int, 
                                 candidate_experience: List[Dict[str, Any]]) -> Tuple[float, str]:
        """
        Calculate an experience match score
        
        Args:
            job_experience: Required years of experience
            candidate_experience: List of candidate's experience entries
            
        Returns:
            Tuple of (score, details)
        """
        try:
            if job_experience <= 0:
                return 100.0, "No experience requirement specified"
            
            # Calculate total years of experience
            total_years = 0
            relevant_years = 0
            experience_details = []
            
            for exp in candidate_experience:
                # Extract duration
                duration = 0
                if isinstance(exp, dict) and 'duration' in exp:
                    duration_str = str(exp['duration'])
                    # Try to extract years from the duration string
                    match = re.search(r'(\d+(?:\.\d+)?)', duration_str)
                    if match:
                        try:
                            duration = float(match.group(1))
                        except ValueError:
                            pass
                
                # If we couldn't extract a duration, assume 1 year
                if duration <= 0:
                    duration = 1
                
                total_years += duration
                
                # Check if experience is relevant (simplified approach)
                relevance = 1.0  # Default full relevance
                experience_details.append(f"{duration} years as {exp.get('title', 'Unknown')} at {exp.get('company', 'Unknown')}")
                
                relevant_years += duration * relevance
            
            # Calculate score based on how the candidate's experience compares to requirements
            if relevant_years >= job_experience:
                # Meets or exceeds requirements
                score = 100.0
                details = f"Candidate has {relevant_years:.1f} years of relevant experience, exceeding the {job_experience} years required.\n"
            else:
                # Partially meets requirements
                score = (relevant_years / job_experience) * 100
                details = f"Candidate has {relevant_years:.1f} years of relevant experience, which is {score:.1f}% of the {job_experience} years required.\n"
            
            # Add experience details
            details += "Experience breakdown:\n" + "\n".join(experience_details)
            
            return score, details
            
        except Exception as e:
            logger.error(f"Error calculating experience score: {e}")
            return 0.0, f"Error in calculation: {str(e)}"
    
    @staticmethod
    def calculate_education_score(job_education: str, 
                                candidate_education: List[Dict[str, Any]]) -> Tuple[float, str]:
        """
        Calculate an education match score
        
        Args:
            job_education: Required education
            candidate_education: List of candidate's education entries
            
        Returns:
            Tuple of (score, details)
        """
        try:
            if not job_education or job_education.lower() == "not specified":
                return 100.0, "No education requirement specified"
            
            # Education level hierarchy (higher index = higher level)
            education_levels = [
                "high school",
                "associate's degree", "associate degree", "associates",
                "bachelor's degree", "bachelor degree", "bachelors", "b.s.", "b.a.",
                "master's degree", "master degree", "masters", "m.s.", "m.a.", "mba",
                "doctorate", "doctoral", "phd", "ph.d."
            ]
            
            # Extract required education level
            required_level = 0
            for i, level in enumerate(education_levels):
                if level in job_education.lower():
                    required_level = i
                    break
            
            # Check candidate's highest education level
            highest_level = 0
            highest_degree = "None"
            degree_details = []
            
            for edu in candidate_education:
                if isinstance(edu, dict):
                    degree = edu.get('degree', '')
                else:
                    degree = str(edu)
                
                degree_details.append(degree)
                
                for i, level in enumerate(education_levels):
                    if level in degree.lower():
                        if i > highest_level:
                            highest_level = i
                            highest_degree = degree
                        break
            
            # Calculate score based on education level comparison
            if highest_level >= required_level:
                score = 100.0
                details = f"Candidate's highest education ({highest_degree}) meets or exceeds the required level ({job_education})."
            else:
                # Scale score based on how close they are to required level
                score = (highest_level / required_level) * 100 if required_level > 0 else 0
                details = f"Candidate's highest education ({highest_degree}) is below the required level ({job_education})."
            
            # Add education details
            details += "\nEducation details:\n" + "\n".join(degree_details)
            
            return score, details
            
        except Exception as e:
            logger.error(f"Error calculating education score: {e}")
            return 0.0, f"Error in calculation: {str(e)}"
    
    @staticmethod
    def calculate_certification_score(job_certifications: List[str], 
                                    candidate_certifications: List[str]) -> Tuple[float, str]:
        """
        Calculate a certification match score
        
        Args:
            job_certifications: Required certifications
            candidate_certifications: Candidate's certifications
            
        Returns:
            Tuple of (score, details)
        """
        try:
            if not job_certifications:
                return 100.0, "No certification requirements specified"
            
            # Normalize certification lists
            job_certs = [c.lower() for c in job_certifications]
            candidate_certs = [c.lower() for c in candidate_certifications]
            
            matched_certs = []
            missing_certs = []
            
            for cert in job_certs:
                # Check for exact match or substring match
                found = False
                for candidate_cert in candidate_certs:
                    if cert in candidate_cert or candidate_cert in cert:
                        matched_certs.append(cert)
                        found = True
                        break
                
                if not found:
                    missing_certs.append(cert)
            
            # Calculate score
            score = (len(matched_certs) / len(job_certs)) * 100 if job_certs else 100.0
            
            # Prepare detailed explanation
            details = []
            
            if matched_certs:
                details.append(f"Matched certifications: {', '.join(matched_certs)}")
            if missing_certs:
                details.append(f"Missing certifications: {', '.join(missing_certs)}")
                
            detail_text = "\n".join(details)
            
            return score, detail_text
            
        except Exception as e:
            logger.error(f"Error calculating certification score: {e}")
            return 0.0, f"Error in calculation: {str(e)}"
    
    @staticmethod
    def calculate_overall_score(scores: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate an overall match score
        
        Args:
            scores: Dict containing individual score components
            
        Returns:
            Dict with overall score and summary
        """
        try:
            # Define weights for each component
            weights = {
                'skills_match': 0.4,
                'experience_match': 0.3,
                'education_match': 0.2,
                'certification_match': 0.1
            }
            
            # Calculate weighted average
            weighted_sum = 0
            used_weights = 0
            
            for component, weight in weights.items():
                if component in scores and 'score' in scores[component]:
                    score = scores[component]['score']
                    weighted_sum += score * weight
                    used_weights += weight
            
            # Calculate final score
            if used_weights > 0:
                overall_score = weighted_sum / used_weights
            else:
                overall_score = 0
            
            # Create summary
            summary_parts = []
            
            if 'skills_match' in scores:
                skill_score = scores['skills_match']['score']
                if skill_score >= 90:
                    summary_parts.append("excellent skill match")
                elif skill_score >= 70:
                    summary_parts.append("good skill match")
                elif skill_score >= 50:
                    summary_parts.append("moderate skill match")
                else:
                    summary_parts.append("poor skill match")
            
            if 'experience_match' in scores:
                exp_score = scores['experience_match']['score']
                if exp_score >= 90:
                    summary_parts.append("highly experienced")
                elif exp_score >= 70:
                    summary_parts.append("well experienced")
                elif exp_score >= 50:
                    summary_parts.append("adequately experienced")
                else:
                    summary_parts.append("insufficiently experienced")
            
            if 'education_match' in scores:
                edu_score = scores['education_match']['score']
                if edu_score >= 90:
                    summary_parts.append("meets education requirements")
                else:
                    summary_parts.append("below education requirements")
            
            # Create final summary
            if overall_score >= 90:
                summary = f"Excellent overall match ({overall_score:.1f}%): " + ", ".join(summary_parts)
            elif overall_score >= 75:
                summary = f"Strong overall match ({overall_score:.1f}%): " + ", ".join(summary_parts)
            elif overall_score >= 60:
                summary = f"Good overall match ({overall_score:.1f}%): " + ", ".join(summary_parts)
            elif overall_score >= 50:
                summary = f"Moderate overall match ({overall_score:.1f}%): " + ", ".join(summary_parts)
            else:
                summary = f"Poor overall match ({overall_score:.1f}%): " + ", ".join(summary_parts)
            
            return {
                'score': overall_score,
                'summary': summary
            }
            
        except Exception as e:
            logger.error(f"Error calculating overall score: {e}")
            return {
                'score': 0,
                'summary': f"Error calculating overall score: {str(e)}"
            }

def calculate_match_scores(job_data: Dict[str, Any], candidate_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate all match scores for a job and candidate
    
    Args:
        job_data: Structured job data
        candidate_data: Structured candidate data
        
    Returns:
        Dict with all match scores
    """
    try:
        # Extract skills
        job_skills = job_data.get('required_skills', {})
        if isinstance(job_skills, str):
            job_skills = {
                'technical_skills': [],
                'soft_skills': []
            }
        
        candidate_skills = candidate_data.get('skills', {})
        
        # Calculate skills score
        skills_score, skills_details = MatchScorer.calculate_skills_score(job_skills, candidate_skills)
        
        # Extract experience
        job_experience = int(job_data.get('required_experience', 0))
        candidate_experience = candidate_data.get('experience', [])
        
        # Calculate experience score
        experience_score, experience_details = MatchScorer.calculate_experience_score(job_experience, candidate_experience)
        
        # Extract education
        job_education = job_data.get('required_education', '')
        candidate_education = candidate_data.get('education', [])
        
        # Calculate education score
        education_score, education_details = MatchScorer.calculate_education_score(job_education, candidate_education)
        
        # Extract certifications
        job_certifications = job_data.get('certifications', [])
        candidate_certifications = candidate_data.get('certifications', [])
        
        # Calculate certification score
        certification_score, certification_details = MatchScorer.calculate_certification_score(job_certifications, candidate_certifications)
        
        # Compile all scores
        scores = {
            'skills_match': {
                'score': skills_score,
                'details': skills_details
            },
            'experience_match': {
                'score': experience_score,
                'details': experience_details
            },
            'education_match': {
                'score': education_score,
                'details': education_details
            },
            'certification_match': {
                'score': certification_score,
                'details': certification_details
            }
        }
        
        # Calculate overall score
        overall = MatchScorer.calculate_overall_score(scores)
        scores['overall_match'] = overall
        
        return scores
        
    except Exception as e:
        logger.error(f"Error calculating match scores: {e}")
        return {
            'skills_match': {'score': 0, 'details': 'Error in calculation'},
            'experience_match': {'score': 0, 'details': 'Error in calculation'},
            'education_match': {'score': 0, 'details': 'Error in calculation'},
            'certification_match': {'score': 0, 'details': 'Error in calculation'},
            'overall_match': {'score': 0, 'summary': f'Error calculating scores: {str(e)}'}
        }

if __name__ == "__main__":
    # Test the scoring functions
    
    # Sample job data
    job_data = {
        'job_title': 'Senior Python Developer',
        'required_experience': 5,
        'required_education': "Bachelor's degree in Computer Science",
        'required_skills': {
            'technical_skills': ['Python', 'Django', 'Flask', 'SQL', 'Git'],
            'soft_skills': ['Communication', 'Teamwork', 'Problem-solving']
        },
        'certifications': ['AWS Certified Developer']
    }
    
    # Sample candidate data
    candidate_data = {
        'name': 'John Smith',
        'education': [
            {'degree': 'Master of Science in Computer Science', 'institution': 'Stanford University', 'year': '2018'},
            {'degree': 'Bachelor of Science in Computer Engineering', 'institution': 'MIT', 'year': '2016'}
        ],
        'experience': [
            {'title': 'Senior Software Engineer', 'company': 'Tech Solutions Inc.', 'duration': '3 years', 
             'description': 'Developed RESTful APIs using Django and Flask'},
            {'title': 'Software Engineer', 'company': 'Innovative Systems', 'duration': '2 years',
             'description': 'Built microservices using Python and Node.js'}
        ],
        'skills': {
            'technical': ['Python', 'JavaScript', 'Django', 'Flask', 'React', 'SQL', 'Git'],
            'soft': ['Communication', 'Teamwork', 'Leadership']
        },
        'certifications': ['AWS Certified Developer', 'Certified Scrum Master']
    }
    
    # Calculate match scores
    scores = calculate_match_scores(job_data, candidate_data)
    
    # Print results
    print(json.dumps(scores, indent=2))
