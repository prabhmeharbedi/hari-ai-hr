"""
Main application file for the AI Recruitment System
"""
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///talent_spotter.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
from database import db
db.init_app(app)

# Import models after db initialization
from models.user import User
from models.job import Job
from models.candidate import Candidate
from models.shortlist import Shortlist, ShortlistCandidate

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import routes after all initialization
from routes import auth, jobs, candidates, shortlists

# Register blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(jobs.bp)
app.register_blueprint(candidates.bp)
app.register_blueprint(shortlists.bp)

@app.route('/')
def index():
    """Home page route"""
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)