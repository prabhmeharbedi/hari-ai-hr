"""
TalentSpotter - AI-powered Recruitment System
"""

import os
from flask import Flask
from .database import db, init_app as init_db
from .routes import init_app as init_routes

__all__ = ['create_app', 'db']

def create_app():
    app = Flask(__name__)
    app.secret_key = 'dev_secret_key'  # Change this in production
    
    # Configure database
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'database.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialize database
    init_db(app)
    
    # Initialize routes
    init_routes(app)
    
    return app 