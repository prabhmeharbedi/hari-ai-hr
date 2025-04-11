"""
Routes for system settings
"""
import logging
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app import db

logger = logging.getLogger(__name__)

# Create blueprint
bp = Blueprint('settings', __name__, url_prefix='/analytics/settings')

# Application settings
APP_SETTINGS = {
    'matching': {
        'threshold_shortlist': 70,
        'skills_weight': 40,
        'experience_weight': 30,
        'education_weight': 20,
        'certifications_weight': 10
    },
    'interface': {
        'items_per_page': 20,
        'date_format': 'YYYY-MM-DD',
        'theme': 'dark'
    },
    'notifications': {
        'email_notifications': True,
        'shortlist_notifications': True,
        'interview_notifications': True
    }
}

@bp.route('/')
def system_settings():
    """Show system settings"""
    logger.debug("Loading system settings page")
    
    # For a real application, these settings would be stored in a database
    # For this prototype, we're using a global variable
    
    return render_template('analytics/settings/index.html', settings=APP_SETTINGS)

@bp.route('/matching', methods=['GET', 'POST'])
def matching_settings():
    """Manage matching algorithm settings"""
    logger.debug("Loading matching settings page")
    
    if request.method == 'POST':
        # Extract form data
        threshold = request.form.get('threshold_shortlist', type=int)
        skills_weight = request.form.get('skills_weight', type=int)
        experience_weight = request.form.get('experience_weight', type=int)
        education_weight = request.form.get('education_weight', type=int)
        certifications_weight = request.form.get('certifications_weight', type=int)
        
        # Validate weights add up to 100
        total_weight = skills_weight + experience_weight + education_weight + certifications_weight
        if total_weight != 100:
            flash('Weights must add up to 100%', 'danger')
            return render_template('analytics/settings/matching.html', settings=APP_SETTINGS['matching'])
        
        # Update settings
        APP_SETTINGS['matching']['threshold_shortlist'] = threshold
        APP_SETTINGS['matching']['skills_weight'] = skills_weight
        APP_SETTINGS['matching']['experience_weight'] = experience_weight
        APP_SETTINGS['matching']['education_weight'] = education_weight
        APP_SETTINGS['matching']['certifications_weight'] = certifications_weight
        
        flash('Matching settings updated successfully', 'success')
        return redirect(url_for('system_settings'))
    
    return render_template('analytics/settings/matching.html', settings=APP_SETTINGS['matching'])

@bp.route('/interface', methods=['GET', 'POST'])
def interface_settings():
    """Manage user interface settings"""
    logger.debug("Loading interface settings page")
    
    if request.method == 'POST':
        # Extract form data
        items_per_page = request.form.get('items_per_page', type=int)
        date_format = request.form.get('date_format')
        theme = request.form.get('theme')
        
        # Update settings
        APP_SETTINGS['interface']['items_per_page'] = items_per_page
        APP_SETTINGS['interface']['date_format'] = date_format
        APP_SETTINGS['interface']['theme'] = theme
        
        flash('Interface settings updated successfully', 'success')
        return redirect(url_for('system_settings'))
    
    return render_template('analytics/settings/interface.html', settings=APP_SETTINGS['interface'])

@bp.route('/notifications', methods=['GET', 'POST'])
def notification_settings():
    """Manage notification settings"""
    logger.debug("Loading notification settings page")
    
    if request.method == 'POST':
        # Extract form data
        email_notifications = 'email_notifications' in request.form
        shortlist_notifications = 'shortlist_notifications' in request.form
        interview_notifications = 'interview_notifications' in request.form
        
        # Update settings
        APP_SETTINGS['notifications']['email_notifications'] = email_notifications
        APP_SETTINGS['notifications']['shortlist_notifications'] = shortlist_notifications
        APP_SETTINGS['notifications']['interview_notifications'] = interview_notifications
        
        flash('Notification settings updated successfully', 'success')
        return redirect(url_for('system_settings'))
    
    return render_template('analytics/settings/notifications.html', settings=APP_SETTINGS['notifications'])

@bp.route('/database')
def database_settings():
    """Database management and statistics"""
    logger.debug("Loading database settings page")
    
    # Get database statistics
    from database.db_operations import get_db_stats
    
    stats = get_db_stats()
    
    # For a production application, you'd also show info about database connection,
    # size, performance metrics, etc.
    
    return render_template('analytics/settings/database.html', stats=stats)

@bp.route('/api/settings')
def api_settings():
    """API endpoint to get current settings"""
    return jsonify(APP_SETTINGS)

# Register blueprint with the application
def init_app(app):
    app.register_blueprint(bp)
    
    # Also register the routes directly with the app for compatibility
    app.add_url_rule('/analytics/settings/', view_func=system_settings)
    app.add_url_rule('/analytics/settings/matching', view_func=matching_settings, methods=['GET', 'POST'])
    app.add_url_rule('/analytics/settings/interface', view_func=interface_settings, methods=['GET', 'POST'])
    app.add_url_rule('/analytics/settings/notifications', view_func=notification_settings, methods=['GET', 'POST'])
    app.add_url_rule('/analytics/settings/database', view_func=database_settings)
    app.add_url_rule('/analytics/settings/api/settings', view_func=api_settings)