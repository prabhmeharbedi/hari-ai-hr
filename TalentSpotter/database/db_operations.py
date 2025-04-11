"""
Database utility functions for the AI Recruitment System
"""
import logging
import os
import json
from sqlalchemy import text, func
from typing import Dict, List, Any, Optional
from database import db
from models.job import Job
from models.candidate import Candidate
from models.match import MatchScore
from models.shortlist import Shortlist
from models.shortlist_candidate import ShortlistCandidate
from models.interview import Interview

logger = logging.getLogger(__name__)

def initialize_database() -> bool:
    """
    Initialize the database with schema and indexes
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create all tables
        db.create_all()
        
        # Read schema.sql for index creation
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Split into statements and filter for index creation
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        index_statements = [stmt for stmt in statements if stmt.upper().startswith('CREATE INDEX')]
        
        # Execute index creation statements
        for stmt in index_statements:
            try:
                db.session.execute(text(stmt))
                db.session.commit()
            except Exception as e:
                logger.warning(f"Warning executing index creation statement: {stmt}\nError: {e}")
                db.session.rollback()
                continue
        
        logger.info("Database schema initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing database schema: {e}")
        db.session.rollback()
        return False

def get_db_stats() -> Dict[str, Any]:
    """
    Get database statistics
    
    Returns:
        Dict containing counts and statistics
    """
    try:
        stats = {
            'jobs': db.session.query(db.func.count('*')).select_from(db.Model.metadata.tables['jobs']).scalar() or 0,
            'candidates': db.session.query(db.func.count('*')).select_from(db.Model.metadata.tables['candidates']).scalar() or 0,
            'matches': db.session.query(db.func.count('*')).select_from(db.Model.metadata.tables['match_scores']).scalar() or 0,
            'shortlists': db.session.query(db.func.count('*')).select_from(db.Model.metadata.tables['shortlists']).scalar() or 0,
            'interviews': db.session.query(db.func.count('*')).select_from(db.Model.metadata.tables['interviews']).scalar() or 0,
            'avg_match_score': db.session.query(db.func.avg(db.Model.metadata.tables['match_scores'].c.overall_score)).scalar() or 0
        }
        return stats
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return {
            'jobs': 0,
            'candidates': 0,
            'matches': 0,
            'shortlists': 0,
            'interviews': 0,
            'avg_match_score': 0
        }

def serialize_json_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert JSON string fields to Python objects
    
    Args:
        data: Dictionary containing data with potential JSON string fields
    
    Returns:
        Dictionary with JSON fields parsed
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
            try:
                result[key] = json.loads(value)
            except json.JSONDecodeError:
                result[key] = value
        else:
            result[key] = value
    return result

def prepare_for_storage(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert Python objects to JSON strings for storage
    
    Args:
        data: Dictionary containing data with potential object fields
    
    Returns:
        Dictionary with object fields converted to JSON strings
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, (dict, list)):
            result[key] = json.dumps(value)
        else:
            result[key] = value
    return result

def execute_raw_query(query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Execute a raw SQL query and return results as a list of dictionaries
    
    Args:
        query: SQL query string
        params: Optional parameters for the query
    
    Returns:
        List of dictionaries containing query results
    """
    try:
        # Execute the query
        result = db.session.execute(text(query), params or {})
        
        # Convert to list of dictionaries
        columns = result.keys()
        rows = []
        for row in result:
            row_dict = {col: val for col, val in zip(columns, row)}
            rows.append(row_dict)
        
        return rows
    except Exception as e:
        logger.error(f"Error executing raw query: {e}")
        db.session.rollback()
        return []