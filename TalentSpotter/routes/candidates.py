"""
Routes for candidate management
"""
import logging
import json
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from models import Candidate
from database import db
from database.db_operations import serialize_json_fields, prepare_for_storage

logger = logging.getLogger(__name__)

# Create blueprint
bp = Blueprint('candidates', __name__, url_prefix='/candidates')

@bp.route('/')
def candidate_list():
    """Show all candidates"""
    logger.debug("Loading candidate list page")
    
    candidates = Candidate.query.all()
    return render_template('candidates/index.html', candidates=candidates)

@bp.route('/add', methods=['GET', 'POST'])
def add_candidate():
    """Add a new candidate"""
    logger.debug("Add candidate page accessed")
    
    if request.method == 'POST':
        # Extract form data
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        # Process education as JSON
        education_json = []
        education_degrees = request.form.getlist('degree[]')
        education_institutions = request.form.getlist('institution[]')
        education_years = request.form.getlist('year[]')
        
        for i in range(len(education_degrees)):
            if education_degrees[i]:
                education_json.append({
                    'degree': education_degrees[i],
                    'institution': education_institutions[i] if i < len(education_institutions) else '',
                    'year': education_years[i] if i < len(education_years) else ''
                })
        
        # Process experience as JSON
        experience_json = []
        experience_titles = request.form.getlist('title[]')
        experience_companies = request.form.getlist('company[]')
        experience_durations = request.form.getlist('duration[]')
        experience_descriptions = request.form.getlist('description[]')
        
        for i in range(len(experience_titles)):
            if experience_titles[i]:
                experience_json.append({
                    'title': experience_titles[i],
                    'company': experience_companies[i] if i < len(experience_companies) else '',
                    'duration': experience_durations[i] if i < len(experience_durations) else '',
                    'description': experience_descriptions[i] if i < len(experience_descriptions) else ''
                })
        
        # Process skills as JSON
        try:
            technical_skills = json.loads(request.form.get('technical_skills', '[]'))
        except json.JSONDecodeError:
            technical_skills = [s.strip() for s in request.form.get('technical_skills', '').split(',') if s.strip()]
            
        try:
            soft_skills = json.loads(request.form.get('soft_skills', '[]'))
        except json.JSONDecodeError:
            soft_skills = [s.strip() for s in request.form.get('soft_skills', '').split(',') if s.strip()]
        
        skills_json = {
            'technical': technical_skills,
            'soft': soft_skills
        }
        
        # Process certifications
        try:
            certifications = json.loads(request.form.get('certifications', '[]'))
        except json.JSONDecodeError:
            certifications = [c.strip() for c in request.form.get('certifications', '').split(',') if c.strip()]
        
        # Get CV text
        cv_text = request.form.get('cv_text', '')
        
        # Create new candidate
        new_candidate = Candidate(
            name=name,
            email=email,
            phone=phone,
            education=json.dumps(education_json),
            experience=json.dumps(experience_json),
            skills=json.dumps(skills_json),
            certifications=json.dumps(certifications),
            cv_text=cv_text
        )
        
        try:
            db.session.add(new_candidate)
            db.session.commit()
            flash('Candidate added successfully!', 'success')
            return redirect(url_for('candidate_list'))
        except Exception as e:
            logger.error(f"Error adding candidate: {e}")
            db.session.rollback()
            flash(f'Error adding candidate: {str(e)}', 'danger')
    
    return render_template('candidates/add.html')

@bp.route('/<int:candidate_id>')
def view_candidate(candidate_id):
    """View a candidate"""
    logger.debug(f"Viewing candidate with ID: {candidate_id}")
    
    candidate = Candidate.query.get_or_404(candidate_id)
    
    # Parse JSON fields
    candidate_data = serialize_json_fields({
        'name': candidate.name,
        'email': candidate.email,
        'phone': candidate.phone,
        'education': candidate.education,
        'experience': candidate.experience,
        'skills': candidate.skills,
        'certifications': candidate.certifications,
        'created_at': candidate.created_at
    })
    
    return render_template('candidates/view.html', candidate=candidate, candidate_data=candidate_data)

@bp.route('/edit/<int:candidate_id>', methods=['GET', 'POST'])
def edit_candidate(candidate_id):
    """Edit an existing candidate"""
    logger.debug(f"Editing candidate with ID: {candidate_id}")
    
    candidate = Candidate.query.get_or_404(candidate_id)
    
    if request.method == 'POST':
        # Extract form data
        candidate.name = request.form.get('name')
        candidate.email = request.form.get('email')
        candidate.phone = request.form.get('phone')
        
        # Process education as JSON
        education_json = []
        education_degrees = request.form.getlist('degree[]')
        education_institutions = request.form.getlist('institution[]')
        education_years = request.form.getlist('year[]')
        
        for i in range(len(education_degrees)):
            if education_degrees[i]:
                education_json.append({
                    'degree': education_degrees[i],
                    'institution': education_institutions[i] if i < len(education_institutions) else '',
                    'year': education_years[i] if i < len(education_years) else ''
                })
        
        # Process experience as JSON
        experience_json = []
        experience_titles = request.form.getlist('title[]')
        experience_companies = request.form.getlist('company[]')
        experience_durations = request.form.getlist('duration[]')
        experience_descriptions = request.form.getlist('description[]')
        
        for i in range(len(experience_titles)):
            if experience_titles[i]:
                experience_json.append({
                    'title': experience_titles[i],
                    'company': experience_companies[i] if i < len(experience_companies) else '',
                    'duration': experience_durations[i] if i < len(experience_durations) else '',
                    'description': experience_descriptions[i] if i < len(experience_descriptions) else ''
                })
        
        # Process skills as JSON
        try:
            technical_skills = json.loads(request.form.get('technical_skills', '[]'))
        except json.JSONDecodeError:
            technical_skills = [s.strip() for s in request.form.get('technical_skills', '').split(',') if s.strip()]
            
        try:
            soft_skills = json.loads(request.form.get('soft_skills', '[]'))
        except json.JSONDecodeError:
            soft_skills = [s.strip() for s in request.form.get('soft_skills', '').split(',') if s.strip()]
        
        skills_json = {
            'technical': technical_skills,
            'soft': soft_skills
        }
        
        # Process certifications
        try:
            certifications = json.loads(request.form.get('certifications', '[]'))
        except json.JSONDecodeError:
            certifications = [c.strip() for c in request.form.get('certifications', '').split(',') if c.strip()]
        
        # Update candidate
        candidate.education = json.dumps(education_json)
        candidate.experience = json.dumps(experience_json)
        candidate.skills = json.dumps(skills_json)
        candidate.certifications = json.dumps(certifications)
        
        # Only update CV text if provided
        if request.form.get('cv_text'):
            candidate.cv_text = request.form.get('cv_text')
        
        try:
            db.session.commit()
            flash('Candidate updated successfully!', 'success')
            return redirect(url_for('view_candidate', candidate_id=candidate.candidate_id))
        except Exception as e:
            logger.error(f"Error updating candidate: {e}")
            db.session.rollback()
            flash(f'Error updating candidate: {str(e)}', 'danger')
    
    # Parse JSON fields for the form
    candidate_data = serialize_json_fields({
        'name': candidate.name,
        'email': candidate.email,
        'phone': candidate.phone,
        'education': candidate.education,
        'experience': candidate.experience,
        'skills': candidate.skills,
        'certifications': candidate.certifications
    })
    
    return render_template('candidates/edit.html', candidate=candidate, candidate_data=candidate_data)

@bp.route('/delete/<int:candidate_id>', methods=['POST'])
def delete_candidate(candidate_id):
    """Delete a candidate"""
    logger.debug(f"Deleting candidate with ID: {candidate_id}")
    
    candidate = Candidate.query.get_or_404(candidate_id)
    
    try:
        db.session.delete(candidate)
        db.session.commit()
        flash('Candidate deleted successfully!', 'success')
    except Exception as e:
        logger.error(f"Error deleting candidate: {e}")
        db.session.rollback()
        flash(f'Error deleting candidate: {str(e)}', 'danger')
    
    return redirect(url_for('candidate_list'))

@bp.route('/bulk-upload', methods=['GET', 'POST'])
def bulk_upload():
    """Handle bulk upload of candidates"""
    logger.debug("Bulk upload page accessed")
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
            
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
            
        if file:
            # Process the uploaded CSV file
            # This is a placeholder for the actual implementation
            flash('Bulk upload feature is coming soon!', 'info')
            
    return render_template('candidates/bulk_upload.html')

@bp.route('/api/count')
def candidate_count():
    """API endpoint to get the count of candidates"""
    count = Candidate.query.count()
    return {'count': count}

# Register blueprint with the application
def init_app(app):
    app.register_blueprint(bp)
    
    # Also register the routes directly with the app for compatibility
    app.add_url_rule('/candidates/', view_func=candidate_list)
    app.add_url_rule('/candidates/add', view_func=add_candidate, methods=['GET', 'POST'])
    app.add_url_rule('/candidates/<int:candidate_id>', view_func=view_candidate)
    app.add_url_rule('/candidates/edit/<int:candidate_id>', view_func=edit_candidate, methods=['GET', 'POST'])
    app.add_url_rule('/candidates/delete/<int:candidate_id>', view_func=delete_candidate, methods=['POST'])
    app.add_url_rule('/candidates/bulk-upload', view_func=bulk_upload, methods=['GET', 'POST'])