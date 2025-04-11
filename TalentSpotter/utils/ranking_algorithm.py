"""
Smart Candidate Ranking Algorithm for AI Recruitment System.

This module provides advanced ranking algorithms for candidates based on
various factors such as skills, experience, education, and certifications.
It includes weighting functions, normalization, and explainability features.
"""

import json
from typing import Dict, List, Any, Tuple, Optional
import numpy as np
from models import Candidate, JobDescription, MatchScore
from utils.openai_integration import explain_ranking


class SmartRankingAlgorithm:
    """
    Smart candidate ranking algorithm with explainable insights.
    
    This class handles the ranking of candidates for a specific job description
    using configurable weights, feature importance, and generates explanations
    for the ranking decisions.
    """
    
    def __init__(
        self,
        job_id: int,
        weight_skills: float = 0.4,
        weight_experience: float = 0.3,
        weight_education: float = 0.2,
        weight_certifications: float = 0.1,
        use_dynamic_weights: bool = True
    ):
        """
        Initialize the ranking algorithm with weights for different factors.
        
        Args:
            job_id: ID of the job description
            weight_skills: Weight for skills match score (0-1)
            weight_experience: Weight for experience match score (0-1)
            weight_education: Weight for education match score (0-1)
            weight_certifications: Weight for certifications match score (0-1)
            use_dynamic_weights: Whether to adjust weights based on job requirements
        """
        self.job_id = job_id
        self.base_weights = {
            'skills': weight_skills,
            'experience': weight_experience,
            'education': weight_education,
            'certifications': weight_certifications
        }
        self.use_dynamic_weights = use_dynamic_weights
        self.job = None
        self.updated_weights = self.base_weights.copy()
        
    def _load_job_description(self) -> JobDescription:
        """Load job description from database."""
        from main import db
        self.job = JobDescription.query.get(self.job_id)
        if not self.job:
            raise ValueError(f"Job description with ID {self.job_id} not found")
        return self.job
        
    def _calculate_dynamic_weights(self) -> Dict[str, float]:
        """
        Calculate dynamic weights based on job requirements.
        
        Returns:
            Dictionary of adjusted weights
        """
        if not self.job:
            self._load_job_description()
            
        weights = self.base_weights.copy()
        
        # Analyze job description to adjust weights
        # For example, if the job has many specific skills listed,
        # increase the weight of skills
        job_skills = self.job.skills_dict()
        if len(job_skills) > 5:
            weights['skills'] += 0.1
            # Normalize other weights
            factor = (1.0 - weights['skills']) / (1.0 - self.base_weights['skills'])
            weights['experience'] = self.base_weights['experience'] * factor
            weights['education'] = self.base_weights['education'] * factor
            weights['certifications'] = self.base_weights['certifications'] * factor
            
        # If there's a high experience requirement, increase weight of experience
        if self.job.required_experience > 5:
            weights['experience'] += 0.1
            # Normalize other weights
            factor = (1.0 - weights['experience']) / (1.0 - self.base_weights['experience'])
            weights['skills'] = self.base_weights['skills'] * factor
            weights['education'] = self.base_weights['education'] * factor
            weights['certifications'] = self.base_weights['certifications'] * factor
        
        # Ensure weights sum to 1.0
        total = sum(weights.values())
        if total > 0:
            weights = {k: v / total for k, v in weights.items()}
            
        self.updated_weights = weights
        return weights
        
    def _calculate_weighted_score(self, match: MatchScore) -> float:
        """
        Calculate weighted overall score based on individual component scores.
        
        Args:
            match: MatchScore object with component scores
            
        Returns:
            Weighted overall score (0-1)
        """
        weights = self.updated_weights if self.use_dynamic_weights else self.base_weights
        
        weighted_score = (
            match.skills_score * weights['skills'] +
            match.experience_score * weights['experience'] +
            match.education_score * weights['education'] +
            match.certifications_score * weights['certifications']
        )
        
        return weighted_score
        
    def rank_candidates(self, explain: bool = True) -> List[Dict[str, Any]]:
        """
        Rank candidates for the job based on match scores.
        
        Args:
            explain: Whether to generate explanations for the ranking
            
        Returns:
            List of ranked candidates with scores and explanations
        """
        if not self.job:
            self._load_job_description()
            
        # If using dynamic weights, calculate them
        if self.use_dynamic_weights:
            self._calculate_dynamic_weights()
            
        # Get all match scores for this job
        from main import db
        matches = MatchScore.query.filter_by(jd_id=self.job_id).all()
        
        # Calculate weighted scores
        candidates_with_scores = []
        for match in matches:
            # Calculate weighted score
            weighted_score = self._calculate_weighted_score(match)
            
            # Get candidate details
            candidate = match.candidate
            
            # Create candidate entry with scores
            candidate_entry = {
                'candidate_id': candidate.candidate_id,
                'name': candidate.name,
                'email': candidate.email,
                'skills': candidate.skills_dict(),
                'experience': candidate.experience_list(),
                'education': candidate.education_list(),
                'certifications': candidate.certifications_list(),
                'overall_score': weighted_score,
                'skills_score': match.skills_score,
                'experience_score': match.experience_score,
                'education_score': match.education_score,
                'certifications_score': match.certifications_score,
                'match_id': match.match_id
            }
            
            candidates_with_scores.append(candidate_entry)
            
        # Sort candidates by weighted score in descending order
        ranked_candidates = sorted(
            candidates_with_scores, 
            key=lambda x: x['overall_score'], 
            reverse=True
        )
        
        # Generate explanation if requested
        if explain and ranked_candidates:
            job_data = {
                'job_title': self.job.job_title,
                'department': self.job.department,
                'required_experience': self.job.required_experience,
                'required_skills': self.job.skills_dict(),
                'jd_id': self.job.jd_id
            }
            
            explanation = explain_ranking(ranked_candidates, job_data)
            
            # Attach explanation to the result
            result = {
                'candidates': ranked_candidates,
                'explanation': explanation,
                'weights_used': self.updated_weights
            }
            
            return result
        else:
            return {
                'candidates': ranked_candidates,
                'weights_used': self.updated_weights
            }
            
    def get_top_candidates(self, limit: int = 5, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Get top candidates above a certain threshold.
        
        Args:
            limit: Maximum number of candidates to return
            threshold: Minimum overall score threshold
            
        Returns:
            List of top candidates
        """
        results = self.rank_candidates(explain=False)
        candidates = results['candidates']
        
        # Filter by threshold and limit
        top_candidates = [
            c for c in candidates if c['overall_score'] >= threshold
        ][:limit]
        
        return top_candidates
        
    def generate_shortlist(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Generate a shortlist of candidates for the job.
        
        Args:
            limit: Maximum number of candidates to include in shortlist
            
        Returns:
            List of shortlisted candidates with scores and reasons
        """
        results = self.rank_candidates(explain=True)
        top_candidates = results['candidates'][:limit]
        explanation = results['explanation']
        
        shortlist = []
        
        # Match candidates with their explanations
        for candidate in top_candidates:
            candidate_number = top_candidates.index(candidate) + 1
            
            # Find matching explanation
            if 'candidate_insights' in explanation:
                for insight in explanation['candidate_insights']:
                    if insight.get('candidate_number') == candidate_number:
                        candidate['strengths'] = insight.get('key_strengths', [])
                        candidate['ranking_reason'] = insight.get('ranking_reason', '')
                        break
            
            shortlist.append(candidate)
            
        return {
            'shortlist': shortlist,
            'explanation': explanation,
            'weights_used': results['weights_used']
        }
