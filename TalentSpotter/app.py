"""
TalentSpotter - AI-powered Recruitment System
"""

import logging
import os
from flask import Flask, render_template
from database import db
from models import Job, Candidate, MatchScore, Shortlist, ShortlistCandidate, Interview
from database import init_app as init_db
from routes import init_app as init_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("Starting application...")

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

app = create_app()

@app.route('/')
def index():
    # Get statistics from the database
    num_jobs = Job.query.count()
    num_candidates = Candidate.query.count()
    num_matches = MatchScore.query.count()
    num_interviews = Interview.query.count()
    
    # Get recent matches
    recent_matches = MatchScore.query.order_by(MatchScore.created_at.desc()).limit(5).all()
    
    # Get upcoming interviews
    upcoming_interviews = Interview.query.order_by(Interview.scheduled_time.asc()).limit(5).all()
    
    return render_template('main/dashboard.html',
                         num_jobs=num_jobs,
                         num_candidates=num_candidates,
                         num_matches=num_matches,
                         num_interviews=num_interviews,
                         recent_matches=recent_matches,
                         upcoming_interviews=upcoming_interviews)

if __name__ == '__main__':
    app.run(port=5000, debug=True)