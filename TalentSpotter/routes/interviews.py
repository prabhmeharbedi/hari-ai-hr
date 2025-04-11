"""
Routes for interview scheduling and management
"""
import logging
import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Interview, Shortlist, Candidate, Job, ShortlistCandidate
from database import db
from database.db_operations import serialize_json_fields, prepare_for_storage

logger = logging.getLogger(__name__)

# Create blueprint
bp = Blueprint('interviews', __name__, url_prefix='/interviews')

@bp.route('/')
def interview_list():
    """Show all scheduled interviews"""
    logger.debug("Loading interview list page")
    
    # Get all interviews with related data
    interviews = db.session.query(
        Interview, Job, Candidate
    ).join(
        Shortlist, Interview.shortlist_id == Shortlist.id
    ).join(
        Job, Shortlist.job_id == Job.id
    ).join(
        ShortlistCandidate, ShortlistCandidate.shortlist_id == Shortlist.id
    ).join(
        Candidate, ShortlistCandidate.candidate_id == Candidate.id
    ).order_by(
        Interview.scheduled_date.desc()
    ).all()
    
    # Format interviews for display
    formatted_interviews = []
    for interview, job, candidate in interviews:
        formatted_interviews.append({
            'id': interview.id,
            'job_title': job.title,
            'department': job.department,
            'candidate_name': candidate.name,
            'candidate_email': candidate.email,
            'scheduled_date': interview.scheduled_date,
            'format': interview.format,
            'status': interview.status,
            'feedback': interview.feedback
        })
    
    return render_template('interviews/index.html', 
                          interviews=formatted_interviews,
                          interview_count=len(interviews))

@bp.route('/upcoming')
def upcoming_interviews():
    """Show upcoming interviews"""
    logger.debug("Loading upcoming interviews page")
    
    # Get all upcoming interviews
    now = datetime.utcnow()
    interviews = db.session.query(
        Interview, Job, Candidate
    ).join(
        Shortlist, Interview.shortlist_id == Shortlist.id
    ).join(
        Job, Shortlist.job_id == Job.id
    ).join(
        ShortlistCandidate, ShortlistCandidate.shortlist_id == Shortlist.id
    ).join(
        Candidate, ShortlistCandidate.candidate_id == Candidate.id
    ).filter(
        Interview.scheduled_date > now,
        Interview.status == 'scheduled'
    ).order_by(
        Interview.scheduled_date
    ).all()
    
    # Format interviews for display
    formatted_interviews = []
    for interview, job, candidate in interviews:
        formatted_interviews.append({
            'id': interview.id,
            'job_title': job.title,
            'department': job.department,
            'candidate_name': candidate.name,
            'candidate_email': candidate.email,
            'scheduled_date': interview.scheduled_date,
            'format': interview.format,
            'status': interview.status
        })
    
    return render_template('interviews/upcoming.html', 
                          interviews=formatted_interviews,
                          interview_count=len(interviews))

@bp.route('/schedule/<int:shortlist_id>', methods=['GET', 'POST'])
def schedule_interview(shortlist_id):
    """Schedule an interview for a shortlisted candidate"""
    logger.debug(f"Scheduling interview for shortlist ID: {shortlist_id}")
    
    # Get shortlist with related data
    shortlist = db.session.query(
        Shortlist, Job, Candidate
    ).join(
        Job, Shortlist.job_id == Job.id
    ).join(
        ShortlistCandidate, ShortlistCandidate.shortlist_id == Shortlist.id
    ).join(
        Candidate, ShortlistCandidate.candidate_id == Candidate.id
    ).filter(
        Shortlist.id == shortlist_id
    ).first()
    
    if not shortlist:
        flash('Shortlist not found', 'error')
        return redirect(url_for('interviews.interview_list'))
    
    if request.method == 'POST':
        try:
            # Get the first date option (we'll use this as the scheduled date)
            date_options = request.form.getlist('date_options')
            if not date_options:
                raise ValueError("No date options provided")
                
            scheduled_datetime = datetime.strptime(date_options[0], '%Y-%m-%dT%H:%M')
            format_type = request.form.get('format')
            special_instructions = request.form.get('special_instructions')
            
            # Create new interview
            new_interview = Interview(
                shortlist_id=shortlist_id,
                scheduled_date=scheduled_datetime,
                format=format_type,
                notes=special_instructions,
                status='scheduled'
            )
            
            db.session.add(new_interview)
            
            # Update shortlist status
            shortlist[0].status = 'interviewing'
            
            db.session.commit()
            
            flash('Interview scheduled successfully!', 'success')
            return redirect(url_for('interviews.interview_list'))
            
        except Exception as e:
            logger.error(f"Error scheduling interview: {e}")
            db.session.rollback()
            flash(f'Error scheduling interview: {str(e)}', 'danger')
    
    # Suggested date/time options (next 5 business days, 9 AM to 5 PM)
    suggested_dates = []
    current_date = datetime.utcnow()
    
    for _ in range(5):
        # Skip to next day
        current_date += timedelta(days=1)
        
        # Skip weekends
        while current_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            current_date += timedelta(days=1)
        
        # Add this date
        suggested_dates.append(current_date.strftime('%Y-%m-%d'))
    
    return render_template('interviews/schedule.html',
                          shortlist=shortlist,
                          suggested_dates=suggested_dates)

@bp.route('/reschedule/<int:interview_id>', methods=['GET', 'POST'])
def reschedule_interview(interview_id):
    """Reschedule an existing interview"""
    logger.debug(f"Rescheduling interview with ID: {interview_id}")
    
    interview = Interview.query.get_or_404(interview_id)
    shortlist = Shortlist.query.get(interview.shortlist_id)
    
    # Get job details
    job = Job.query.get(shortlist.job_id)
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('interviews.index'))
    
    if request.method == 'POST':
        # Extract form data
        scheduled_date_str = request.form.get('scheduled_date')
        scheduled_time_str = request.form.get('scheduled_time')
        format_type = request.form.get('format')
        
        # Parse date and time
        try:
            # Combine date and time
            scheduled_datetime_str = f"{scheduled_date_str} {scheduled_time_str}"
            scheduled_datetime = datetime.strptime(scheduled_datetime_str, '%Y-%m-%d %H:%M')
            
            # Update interview
            interview.scheduled_date = scheduled_datetime
            interview.format = format_type
            interview.status = 'rescheduled'
            
            db.session.commit()
            
            # Send email notification (placeholder)
            # This would normally use an email service
            flash('Interview rescheduled and notification email sent!', 'success')
            
            return redirect(url_for('interviews.index'))
        except Exception as e:
            logger.error(f"Error rescheduling interview: {e}")
            db.session.rollback()
            flash(f'Error rescheduling interview: {str(e)}', 'danger')
    
    # Current scheduled date in the expected format
    current_date = interview.scheduled_date.strftime('%Y-%m-%d')
    current_time = interview.scheduled_date.strftime('%H:%M')
    
    # Suggested date/time options (next 5 business days, 9 AM to 5 PM)
    suggested_dates = []
    current_date_obj = datetime.utcnow()
    
    for _ in range(5):
        # Skip to next day
        current_date_obj += timedelta(days=1)
        
        # Skip weekends
        while current_date_obj.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            current_date_obj += timedelta(days=1)
        
        # Add this date
        suggested_dates.append(current_date_obj.strftime('%Y-%m-%d'))
    
    return render_template('interviews/reschedule.html',
                          interview=interview,
                          shortlist=shortlist,
                          job=job,
                          current_date=current_date,
                          current_time=current_time,
                          suggested_dates=suggested_dates)

@bp.route('/cancel/<int:interview_id>', methods=['POST'])
def cancel_interview(interview_id):
    """Cancel an interview"""
    logger.debug(f"Cancelling interview with ID: {interview_id}")
    
    interview = Interview.query.get_or_404(interview_id)
    
    try:
        # Update interview status
        interview.status = 'cancelled'
        
        # Update shortlist status if needed
        shortlist = Shortlist.query.get(interview.shortlist_id)
        
        # If there are no other scheduled interviews for this shortlist,
        # revert the shortlist status to pending
        other_interviews = Interview.query.filter(
            Interview.shortlist_id == shortlist.id,
            Interview.id != interview_id,
            Interview.status == 'scheduled'
        ).count()
        
        if other_interviews == 0:
            shortlist.status = 'pending'
        
        db.session.commit()
        
        # Send email notification (placeholder)
        flash('Interview cancelled and notification email sent!', 'success')
    except Exception as e:
        logger.error(f"Error cancelling interview: {e}")
        db.session.rollback()
        flash(f'Error cancelling interview: {str(e)}', 'danger')
    
    return redirect(url_for('interviews.index'))

@bp.route('/feedback/<int:interview_id>', methods=['GET', 'POST'])
def interview_feedback(interview_id):
    """Provide feedback for a completed interview"""
    logger.debug(f"Adding feedback for interview with ID: {interview_id}")
    
    interview = Interview.query.get_or_404(interview_id)
    shortlist = Shortlist.query.get(interview.shortlist_id)
    
    # Get job details
    job = Job.query.get(shortlist.job_id)
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('interviews.index'))
    
    if request.method == 'POST':
        # Extract form data
        feedback = request.form.get('feedback')
        decision = request.form.get('decision')
        
        try:
            # Update interview
            interview.feedback = feedback
            interview.status = 'completed'
            
            # Update shortlist status based on decision
            shortlist.status = decision
            
            db.session.commit()
            
            flash('Interview feedback saved successfully!', 'success')
            return redirect(url_for('interviews.index'))
        except Exception as e:
            logger.error(f"Error saving feedback: {e}")
            db.session.rollback()
            flash(f'Error saving feedback: {str(e)}', 'danger')
    
    return render_template('interviews/feedback.html',
                          interview=interview,
                          shortlist=shortlist,
                          job=job)

@bp.route('/<int:interview_id>')
def view_interview(interview_id):
    """View interview details"""
    logger.debug(f"Viewing interview with ID: {interview_id}")
    
    # Get interview with related data
    interview_data = db.session.query(
        Interview, Job, Candidate
    ).join(
        Shortlist, Interview.shortlist_id == Shortlist.id
    ).join(
        Job, Shortlist.job_id == Job.id
    ).join(
        ShortlistCandidate, ShortlistCandidate.shortlist_id == Shortlist.id
    ).join(
        Candidate, ShortlistCandidate.candidate_id == Candidate.id
    ).filter(
        Interview.id == interview_id
    ).first_or_404()
    
    interview, job, candidate = interview_data
    
    # Format data for rendering
    formatted_data = {
        'id': interview.id,
        'scheduled_date': interview.scheduled_date,
        'format': interview.format,
        'status': interview.status,
        'feedback': interview.feedback,
        'created_at': interview.created_at,
        'job_title': job.title,
        'department': job.department,
        'candidate_name': candidate.name,
        'candidate_email': candidate.email
    }
    
    return render_template('interviews/view.html',
                          interview=interview,
                          interview_data=formatted_data,
                          job=job,
                          candidate=candidate)

@bp.route('/api/count')
def interview_count():
    """API endpoint to get the count of interviews"""
    count = Interview.query.count()
    return {'count': count}

# Register blueprint with the application
def init_app(app):
    app.register_blueprint(bp)
    
    # Also register the routes directly with the app for compatibility
    app.add_url_rule('/interviews/', view_func=interview_list)
    app.add_url_rule('/interviews/upcoming', view_func=upcoming_interviews)
    app.add_url_rule('/interviews/schedule/<int:shortlist_id>', view_func=schedule_interview, methods=['GET', 'POST'])
    app.add_url_rule('/interviews/reschedule/<int:interview_id>', view_func=reschedule_interview, methods=['GET', 'POST'])
    app.add_url_rule('/interviews/cancel/<int:interview_id>', view_func=cancel_interview, methods=['POST'])
    app.add_url_rule('/interviews/feedback/<int:interview_id>', view_func=interview_feedback, methods=['GET', 'POST'])
    app.add_url_rule('/interviews/<int:interview_id>', view_func=view_interview)