"""
OpenAI API integration utilities for enhanced AI insights.

This module provides functions to leverage OpenAI's advanced capabilities
for generating more accurate and detailed insights for the AI recruitment system.
"""

import os
import json
from typing import Dict, Any, List, Optional

import httpx

def generate_candidate_insights(
    candidate_data: Dict[str, Any], 
    job_data: Dict[str, Any], 
    match_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate detailed insights about a candidate's fit for a job using OpenAI.
    
    Args:
        candidate_data: Dictionary containing candidate information
        job_data: Dictionary containing job description information
        match_data: Dictionary containing match score information
        
    Returns:
        Dictionary containing generated insights with detailed analysis
    """
    # Get API key from environment
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    # Format the data for the prompt
    prompt = f"""
    You are an expert recruitment consultant analyzing a candidate for a job position.
    
    JOB DESCRIPTION:
    {json.dumps(job_data, indent=2)}
    
    CANDIDATE PROFILE:
    {json.dumps(candidate_data, indent=2)}
    
    MATCH SCORES:
    {json.dumps(match_data, indent=2)}
    
    Based on the above information, provide a detailed analysis with the following sections:
    
    1. Strengths (list the top 3-5 strengths of this candidate for this role)
    2. Gaps (identify 2-4 skill or experience gaps that might be concerning)
    3. Cultural Fit (assess potential cultural fit based on their background)
    4. Interview Questions (suggest 3-5 specific questions to ask this candidate)
    5. Development Areas (suggest 2-3 areas for professional development if hired)
    6. Hiring Recommendation (provide a recommendation on a scale: Strongly Recommend, Recommend, Consider, Not Recommended)
    
    Your analysis should be structured, data-driven, and specific to this candidate and job.
    Format your response as JSON with these exact keys: strengths, gaps, cultural_fit, interview_questions, development_areas, hiring_recommendation.
    The values for strengths, gaps, interview_questions, and development_areas should be arrays of strings.
    The values for cultural_fit and hiring_recommendation should be strings.
    """
    
    try:
        # Make request to OpenAI API
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        data = {
            "model": "gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            "messages": [
                {"role": "system", "content": "You are an expert recruitment consultant providing analysis in JSON format."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "response_format": {"type": "json_object"}
        }
        
        # Send request
        response = httpx.post(url, headers=headers, json=data, timeout=30.0)
        response.raise_for_status()
        result = response.json()
        
        # Extract the content
        content = result["choices"][0]["message"]["content"]
        insights = json.loads(content)
        
        return insights
        
    except Exception as e:
        raise Exception(f"Error calling OpenAI API: {str(e)}")

def generate_candidate_ranking_explanation(
    job_data: Dict[str, Any],
    candidates_data: List[Dict[str, Any]],
    match_scores: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate an explanation of the ranking algorithm's decision making process.
    
    Args:
        job_data: Dictionary containing job description information
        candidates_data: List of dictionaries containing candidate information
        match_scores: List of dictionaries containing match score information
        
    Returns:
        Dictionary containing the explanation of the ranking algorithm
    """
    # Get API key from environment
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    # Format the data for the prompt
    prompt = f"""
    You are an expert recruitment algorithm explainer. You need to explain the ranking decisions 
    made by an AI recruitment system for candidates applying to a job.
    
    JOB DESCRIPTION:
    {json.dumps(job_data, indent=2)}
    
    CANDIDATES (Top 10 shown):
    {json.dumps(candidates_data[:10], indent=2)}
    
    MATCH SCORES:
    {json.dumps(match_scores[:10], indent=2)}
    
    Analyze the match scores and candidate profiles to provide a detailed explanation of:
    
    1. How the ranking algorithm works in general
    2. What factors were most important for this specific job
    3. Why certain candidates ranked higher than others
    4. What tie-breakers were used for similarly scored candidates
    5. Individual insights about why each candidate received their specific ranking
    
    Format your response as JSON with these exact keys:
    - ranking_explanation (string): General explanation of how the algorithm works
    - weights_used (object): The weights that were most appropriate for this job
    - differentiation_factors (array): List of factors that differentiated top candidates
    - tie_breakers (array): List of tie-breakers used for similarly scored candidates
    - candidate_insights (array): Array of objects containing insights for each candidate
    
    For weights_used, include these keys with values that sum to 1.0:
    - skills: number between 0 and 1
    - experience: number between 0 and 1
    - education: number between 0 and 1 
    - certifications: number between 0 and 1
    
    For each candidate_insight object, include:
    - candidate_number: position in the ranking (1, 2, 3, etc.)
    - key_strengths: array of strings
    - ranking_reason: string explaining why this candidate received this specific ranking
    """
    
    try:
        # Make request to OpenAI API
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        data = {
            "model": "gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            "messages": [
                {"role": "system", "content": "You are an expert recruitment algorithm explainer providing analysis in JSON format."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "response_format": {"type": "json_object"}
        }
        
        # Send request
        response = httpx.post(url, headers=headers, json=data, timeout=30.0)
        response.raise_for_status()
        result = response.json()
        
        # Extract the content
        content = result["choices"][0]["message"]["content"]
        explanation = json.loads(content)
        
        return explanation
        
    except Exception as e:
        raise Exception(f"Error calling OpenAI API: {str(e)}")
