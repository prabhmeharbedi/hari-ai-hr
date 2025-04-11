"""
Main routes for the AI Recruitment System
"""
import logging
from flask import Blueprint, render_template, redirect, url_for
from database.db_operations import get_db_stats

logger = logging.getLogger(__name__)

# Create blueprint
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Show the main dashboard"""
    logger.debug("Loading main dashboard")
    
    # Get database statistics
    stats = get_db_stats()
    
    return render_template('main/dashboard.html',
                          stats=stats)

def init_app(app):
    """Initialize the main blueprint with the app"""
    app.register_blueprint(bp) 