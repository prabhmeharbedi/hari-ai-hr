"""
Routes for match management
"""
import logging
import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import Job, Candidate, MatchScore, Shortlist
from database import db
from sqlalchemy import text
from database.db_operations import serialize_json_fields, prepare_for_storage

logger = logging.getLogger(__name__)

# Create blueprint
bp = Blueprint('matches', __name__, url_prefix='/matches')

@bp.route('/')
def match_dashboard():
    """Show the matches dashboard"""
    logger.debug("Loading matches dashboard")
    
    # Get stats for the dashboard
    match_count = MatchScore.query.count()
    job_count = Job.query.count()
    candidate_count = Candidate.query.count()
    
    # Get average match score
    avg_score_query = db.session.query(db.func.avg(MatchScore.overall_score)).scalar()
    avg_score = round(float(avg_score_query), 1) if avg_score_query else 0
    
    # Get recent matches
    recent_matches = db.session.query(
        MatchScore, Job.title, Candidate.name
    ).join(
        Job, MatchScore.job_id == Job.id
    ).join(
        Candidate, MatchScore.candidate_id == Candidate.id
    ).order_by(
        MatchScore.created_at.desc()
    ).limit(10).all()
    
    # Format matches for display
    formatted_matches = []
    for match, job_title, candidate_name in recent_matches:
        formatted_matches.append({
            'match_id': match.id,
            'job_title': job_title,
            'candidate_name': candidate_name,
            'score': int(match.overall_score),
            'date': match.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    # Get jobs with matches
    jobs_with_matches = db.session.query(
        Job.id, 
        Job.title,
        db.func.count(MatchScore.id).label('match_count')
    ).outerjoin(
        MatchScore, Job.id == MatchScore.job_id
    ).group_by(
        Job.id
    ).order_by(
        text('match_count DESC')
    ).limit(5).all()
    
    return render_template('matches/dashboard.html',
                          match_count=match_count,
                          job_count=job_count,
                          candidate_count=candidate_count,
                          avg_score=avg_score,
                          recent_matches=formatted_matches,
                          jobs_with_matches=jobs_with_matches)

@bp.route('/job/<int:job_id>')
def job_matches(job_id):
    """Show matches for a specific job"""
    logger.debug(f"Viewing matches for job ID: {job_id}")
    
    job = Job.query.get_or_404(job_id)
    
    # Get all matches for this job
    matches = db.session.query(
        MatchScore, Candidate
    ).join(
        Candidate, MatchScore.candidate_id == Candidate.id
    ).filter(
        MatchScore.job_id == job_id
    ).order_by(
        MatchScore.overall_score.desc()
    ).all()
    
    # Check if candidates are shortlisted
    shortlisted_candidates = {s.candidate_id: s for s in Shortlist.query.filter_by(job_id=job_id).all()}
    
    # Format matches for display
    formatted_matches = []
    for match, candidate in matches:
        is_shortlisted = candidate.id in shortlisted_candidates
        shortlist_status = shortlisted_candidates[candidate.id].status if is_shortlisted else None
        
        formatted_matches.append({
            'match_id': match.id,
            'candidate_id': candidate.id,
            'candidate_name': candidate.name,
            'candidate_email': candidate.email,
            'overall_score': int(match.overall_score),
            'skills_score': int(match.skills_score),
            'experience_score': int(match.experience_score),
            'education_score': int(match.education_score),
            'certifications_score': int(match.certifications_score),
            'is_shortlisted': is_shortlisted,
            'shortlist_status': shortlist_status
        })
    
    return render_template('matches/job_matches.html', 
                          job=job, 
                          matches=formatted_matches,
                          match_count=len(matches))

@bp.route('/candidate/<int:candidate_id>')
def candidate_matches(candidate_id):
    """Show matches for a specific candidate"""
    logger.debug(f"Viewing matches for candidate ID: {candidate_id}")
    
    candidate = Candidate.query.get_or_404(candidate_id)
    
    # Get all matches for this candidate
    matches = db.session.query(
        MatchScore, Job
    ).join(
        Job, MatchScore.job_id == Job.id
    ).filter(
        MatchScore.candidate_id == candidate_id
    ).order_by(
        MatchScore.overall_score.desc()
    ).all()
    
    # Check if candidate is shortlisted for jobs
    shortlisted_jobs = {s.job_id: s for s in Shortlist.query.filter_by(candidate_id=candidate_id).all()}
    
    # Format matches for display
    formatted_matches = []
    for match, job in matches:
        is_shortlisted = job.id in shortlisted_jobs
        shortlist_status = shortlisted_jobs[job.id].status if is_shortlisted else None
        
        formatted_matches.append({
            'match_id': match.id,
            'job_id': job.id,
            'job_title': job.title,
            'department': job.department,
            'overall_score': int(match.overall_score),
            'skills_score': int(match.skills_score),
            'experience_score': int(match.experience_score),
            'education_score': int(match.education_score),
            'certifications_score': int(match.certifications_score),
            'is_shortlisted': is_shortlisted,
            'shortlist_status': shortlist_status
        })
    
    return render_template('matches/candidate_matches.html', 
                          candidate=candidate, 
                          matches=formatted_matches,
                          match_count=len(matches))

@bp.route('/generate/<int:job_id>')
def generate_matches(job_id):
    """Generate matches for a specific job"""
    logger.debug(f"Generating matches for job ID: {job_id}")
    
    if job_id == 0:
        # Generate matches for all jobs
        jobs = Job.query.filter_by(status='active').all()
        flash(f'Match generation started for {len(jobs)} jobs', 'info')
        return redirect(url_for('match_dashboard'))
    
    job = Job.query.get_or_404(job_id)
    
    # Get all candidates
    candidates = Candidate.query.all()
    
    # This would normally use AI agents to calculate match scores
    # For now, we'll use a simple placeholder implementation
    from random import randint
    
    for candidate in candidates:
        # Check if match already exists
        existing_match = MatchScore.query.filter_by(job_id=job_id, candidate_id=candidate.id).first()
        
        if existing_match:
            # Update existing match
            existing_match.overall_score = randint(50, 95)
            existing_match.skills_score = randint(40, 100)
            existing_match.experience_score = randint(40, 100)
            existing_match.education_score = randint(40, 100)
            existing_match.certifications_score = randint(40, 100)
        else:
            # Create new match
            new_match = MatchScore(
                job_id=job_id,
                candidate_id=candidate.id,
                overall_score=randint(50, 95),
                skills_score=randint(40, 100),
                experience_score=randint(40, 100),
                education_score=randint(40, 100),
                certifications_score=randint(40, 100)
            )
            db.session.add(new_match)
    
    try:
        db.session.commit()
        flash(f'Successfully generated matches for {len(candidates)} candidates', 'success')
    except Exception as e:
        logger.error(f"Error generating matches: {e}")
        db.session.rollback()
        flash(f'Error generating matches: {str(e)}', 'danger')
    
    return redirect(url_for('job_matches', job_id=job_id))

@bp.route('/api/details/<int:match_id>')
def get_match_details(match_id):
    """API endpoint to get detailed match information"""
    match = MatchScore.query.get_or_404(match_id)
    
    # Get job and candidate
    job = Job.query.get(match.job_id)
    candidate = Candidate.query.get(match.candidate_id)
    
    # Parse JSON fields
    job_data = serialize_json_fields({
        'job_title': job.title,
        'department': job.department,
        'required_skills': job.required_skills,
        'required_experience': job.required_experience,
        'required_education': job.required_education
    })
    
    candidate_data = serialize_json_fields({
        'name': candidate.name,
        'email': candidate.email,
        'skills': candidate.skills,
        'experience': candidate.experience,
        'education': candidate.education,
        'certifications': candidate.certifications
    })
    
    # Match scores
    scores = {
        'overall': int(match.overall_score),
        'skills': int(match.skills_score),
        'experience': int(match.experience_score),
        'education': int(match.education_score),
        'certifications': int(match.certifications_score),
    }
    
    # Detailed analysis (placeholder)
    # This would normally be generated using AI
    analysis = {
        'skills_match': {
            'matched': ['Python', 'SQL', 'Data Analysis'],
            'missing': ['Machine Learning', 'AWS']
        },
        'experience_match': {
            'years_required': job.required_experience,
            'years_candidate': 5,  # Placeholder
            'analysis': 'Candidate meets the experience requirements'
        },
        'education_match': {
            'required': job_data['required_education'],
            'candidate': candidate_data['education'][0]['degree'] if candidate_data['education'] else 'Not specified',
            'analysis': 'Candidate meets the education requirements'
        }
    }
    
    return jsonify({
        'match_id': match_id,
        'job': job_data,
        'candidate': candidate_data,
        'scores': scores,
        'analysis': analysis,
        'match_date': match.created_at.strftime('%Y-%m-%d %H:%M')
    })

@bp.route('/shortlist/<int:match_id>', methods=['POST'])
def shortlist_candidate(match_id):
    """Shortlist a candidate for a job"""
    logger.debug(f"Shortlisting candidate from match ID: {match_id}")
    
    match = MatchScore.query.get_or_404(match_id)
    
    # Check if already shortlisted
    existing = Shortlist.query.filter_by(job_id=match.job_id, candidate_id=match.candidate_id).first()
    
    if existing:
        flash('This candidate is already shortlisted for this job', 'warning')
    else:
        # Create new shortlist entry
        shortlist = Shortlist(
            job_id=match.job_id,
            candidate_id=match.candidate_id,
            notes=f"Shortlisted with match score: {match.overall_score}%"
        )
        
        try:
            db.session.add(shortlist)
            db.session.commit()
            flash('Candidate has been shortlisted successfully!', 'success')
        except Exception as e:
            logger.error(f"Error shortlisting candidate: {e}")
            db.session.rollback()
            flash(f'Error shortlisting candidate: {str(e)}', 'danger')
    
    return redirect(url_for('job_matches', job_id=match.job_id))

# Register blueprint with the application
def init_app(app):
    app.register_blueprint(bp)
    
    # Also register the routes directly with the app for compatibility
    app.add_url_rule('/matches/', view_func=match_dashboard)
    app.add_url_rule('/matches/job/<int:job_id>', view_func=job_matches)
    app.add_url_rule('/matches/candidate/<int:candidate_id>', view_func=candidate_matches)
    app.add_url_rule('/matches/generate/<int:job_id>', view_func=generate_matches)
    app.add_url_rule('/matches/api/details/<int:match_id>', view_func=get_match_details)
    app.add_url_rule('/matches/shortlist/<int:match_id>', view_func=shortlist_candidate, methods=['POST'])