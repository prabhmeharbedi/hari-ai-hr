"""
Models package for the AI Recruitment System
"""

from .job import Job
from .candidate import Candidate
from .match import MatchScore
from .shortlist import Shortlist
from .shortlist_candidate import ShortlistCandidate
from .interview import Interview

__all__ = ['Job', 'Candidate', 'MatchScore', 'Shortlist', 'ShortlistCandidate', 'Interview'] 