"""
Database module for the AI Recruitment System
"""
import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask import Flask

# Configure logging
logger = logging.getLogger(__name__)

# Create SQLAlchemy base class
class Base(DeclarativeBase):
    pass

# Create the SQLAlchemy instance
db = SQLAlchemy(model_class=Base)

def init_app(app: Flask):
    """Initialize the database with the Flask app"""
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Initialize database schema
        from .db_operations import initialize_database
        initialize_database()
        
    return db

logger.info("Database module loaded")

__all__ = ['db', 'init_app']