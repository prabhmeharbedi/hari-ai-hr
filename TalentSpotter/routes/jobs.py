"""
Routes for job description management
"""
import logging
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Job
from database import db
from database.db_operations import serialize_json_fields, prepare_for_storage

logger = logging.getLogger(__name__)

# Create blueprint
bp = Blueprint('jobs', __name__, url_prefix='/jobs')

@bp.route('/')
def job_list():
    """Show all job descriptions"""
    logger.debug("Loading job list page")
    
    jobs = Job.query.all()
    return render_template('jobs/index.html', jobs=jobs)

@bp.route('/add', methods=['GET', 'POST'])
def add_job():
    """Add a new job description"""
    logger.debug("Add job page accessed")
    
    if request.method == 'POST':
        # Extract form data
        job_title = request.form.get('job_title')
        department = request.form.get('department')
        required_experience = request.form.get('required_experience')
        required_education = request.form.get('required_education')
        
        # Process skills as JSON
        technical_skills = request.form.get('technical_skills', '[]')
        soft_skills = request.form.get('soft_skills', '[]')
        
        # Try to parse as JSON, if not, assume comma-separated values
        try:
            tech_skills_list = json.loads(technical_skills)
        except json.JSONDecodeError:
            tech_skills_list = [s.strip() for s in technical_skills.split(',') if s.strip()]
            
        try:
            soft_skills_list = json.loads(soft_skills)
        except json.JSONDecodeError:
            soft_skills_list = [s.strip() for s in soft_skills.split(',') if s.strip()]
        
        # Combine into skills JSON
        skills = {
            'technical_skills': tech_skills_list,
            'soft_skills': soft_skills_list
        }
        
        # Get responsibilities
        responsibilities = request.form.get('responsibilities')
        responsibilities_list = [r.strip() for r in responsibilities.split('\n') if r.strip()]
        
        # Create new job
        new_job = Job(
            title=job_title,
            department=department,
            required_experience=int(required_experience) if required_experience else None,
            required_education=required_education,
            required_skills=json.dumps(skills),
            job_responsibilities=json.dumps(responsibilities_list)
        )
        
        try:
            db.session.add(new_job)
            db.session.commit()
            flash('Job description added successfully!', 'success')
            return redirect(url_for('job_list'))
        except Exception as e:
            logger.error(f"Error adding job: {e}")
            db.session.rollback()
            flash(f'Error adding job: {str(e)}', 'danger')
    
    return render_template('jobs/add.html')

@bp.route('/<int:job_id>')
def view_job(job_id):
    """View a job description"""
    logger.debug(f"Viewing job with ID: {job_id}")
    
    job = Job.query.get_or_404(job_id)
    
    # Parse JSON fields
    job_data = serialize_json_fields({
        'job_title': job.title,
        'department': job.department,
        'required_experience': job.required_experience,
        'required_education': job.required_education,
        'required_skills': job.required_skills,
        'job_responsibilities': job.job_responsibilities,
        'status': job.status,
        'created_at': job.created_at
    })
    
    return render_template('jobs/view.html', job=job, job_data=job_data)

@bp.route('/edit/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    """Edit a job description"""
    logger.debug(f"Editing job with ID: {job_id}")
    
    job = Job.query.get_or_404(job_id)
    
    if request.method == 'POST':
        # Extract form data
        job.title = request.form.get('job_title')
        job.department = request.form.get('department')
        job.required_experience = int(request.form.get('required_experience')) if request.form.get('required_experience') else None
        job.required_education = request.form.get('required_education')
        
        # Process skills as JSON
        technical_skills = request.form.get('technical_skills', '[]')
        soft_skills = request.form.get('soft_skills', '[]')
        
        # Try to parse as JSON, if not, assume comma-separated values
        try:
            tech_skills_list = json.loads(technical_skills)
        except json.JSONDecodeError:
            tech_skills_list = [s.strip() for s in technical_skills.split(',') if s.strip()]
            
        try:
            soft_skills_list = json.loads(soft_skills)
        except json.JSONDecodeError:
            soft_skills_list = [s.strip() for s in soft_skills.split(',') if s.strip()]
        
        # Combine into skills JSON
        skills = {
            'technical_skills': tech_skills_list,
            'soft_skills': soft_skills_list
        }
        
        # Get responsibilities
        responsibilities = request.form.get('responsibilities')
        responsibilities_list = [r.strip() for r in responsibilities.split('\n') if r.strip()]
        
        # Update job
        job.required_skills = json.dumps(skills)
        job.job_responsibilities = json.dumps(responsibilities_list)
        job.status = request.form.get('status', 'active')
        
        try:
            db.session.commit()
            flash('Job description updated successfully!', 'success')
            return redirect(url_for('view_job', job_id=job.id))
        except Exception as e:
            logger.error(f"Error updating job: {e}")
            db.session.rollback()
            flash(f'Error updating job: {str(e)}', 'danger')
    
    # Parse JSON fields for the template
    job_data = serialize_json_fields({
        'job_title': job.title,
        'department': job.department,
        'required_experience': job.required_experience,
        'required_education': job.required_education,
        'required_skills': job.required_skills,
        'job_responsibilities': job.job_responsibilities,
        'status': job.status
    })
    
    return render_template('jobs/edit.html', job=job, job_data=job_data)

@bp.route('/delete/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    """Delete a job description"""
    logger.debug(f"Deleting job with ID: {job_id}")
    
    job = Job.query.get_or_404(job_id)
    
    try:
        db.session.delete(job)
        db.session.commit()
        flash('Job description deleted successfully!', 'success')
    except Exception as e:
        logger.error(f"Error deleting job: {e}")
        db.session.rollback()
        flash(f'Error deleting job: {str(e)}', 'danger')
    
    return redirect(url_for('job_list'))

@bp.route('/analyze/<int:job_id>')
def analyze_job(job_id):
    """Analyze a job description using AI"""
    logger.debug(f"Analyzing job with ID: {job_id}")
    
    job = Job.query.get_or_404(job_id)
    
    # This will be enhanced with actual AI analysis in the future
    flash('Job analysis feature is coming soon!', 'info')
    
    return redirect(url_for('view_job', job_id=job.id))

# Register blueprint with the application
def init_app(app):
    app.register_blueprint(bp)
    
    # Also register the routes directly with the app for compatibility
    app.add_url_rule('/jobs/', view_func=job_list)
    app.add_url_rule('/jobs/add', view_func=add_job, methods=['GET', 'POST'])
    app.add_url_rule('/jobs/<int:job_id>', view_func=view_job)
    app.add_url_rule('/jobs/edit/<int:job_id>', view_func=edit_job, methods=['GET', 'POST'])
    app.add_url_rule('/jobs/delete/<int:job_id>', view_func=delete_job, methods=['POST'])
    app.add_url_rule('/jobs/analyze/<int:job_id>', view_func=analyze_job)