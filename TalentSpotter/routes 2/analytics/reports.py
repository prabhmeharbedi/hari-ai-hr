"""
Routes for analytics reports
"""
import logging
import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import func, text
from models import JobDescription, Candidate, MatchScore, Shortlist, Interview
from app import db

logger = logging.getLogger(__name__)

# Create blueprint
bp = Blueprint('reports', __name__, url_prefix='/analytics/reports')

@bp.route('/')
def reports_dashboard():
    """Show the reports dashboard"""
    logger.debug("Loading reports dashboard")
    
    # Get basic stats
    stats = {}
    
    # Total counts
    stats['total_jobs'] = JobDescription.query.count()
    stats['total_candidates'] = Candidate.query.count()
    stats['total_matches'] = MatchScore.query.count()
    stats['total_shortlisted'] = Shortlist.query.count()
    stats['total_interviews'] = Interview.query.count()
    
    # Jobs by status
    job_status = db.session.query(
        JobDescription.status, 
        func.count(JobDescription.jd_id)
    ).group_by(
        JobDescription.status
    ).all()
    
    stats['jobs_by_status'] = {status: count for status, count in job_status}
    
    # Shortlists by status
    shortlist_status = db.session.query(
        Shortlist.status, 
        func.count(Shortlist.shortlist_id)
    ).group_by(
        Shortlist.status
    ).all()
    
    stats['shortlists_by_status'] = {status: count for status, count in shortlist_status}
    
    # Interviews by status
    interview_status = db.session.query(
        Interview.status, 
        func.count(Interview.interview_id)
    ).group_by(
        Interview.status
    ).all()
    
    stats['interviews_by_status'] = {status: count for status, count in interview_status}
    
    # Get top 5 jobs by match count
    top_jobs = db.session.query(
        JobDescription.job_title,
        func.count(MatchScore.match_id).label('match_count')
    ).join(
        MatchScore, 
        JobDescription.jd_id == MatchScore.jd_id
    ).group_by(
        JobDescription.job_title
    ).order_by(
        text('match_count DESC')
    ).limit(5).all()
    
    stats['top_jobs'] = [{'title': title, 'count': count} for title, count in top_jobs]
    
    # Get top 5 shortlisted jobs
    top_shortlisted = db.session.query(
        JobDescription.job_title,
        func.count(Shortlist.shortlist_id).label('shortlist_count')
    ).join(
        Shortlist, 
        JobDescription.jd_id == Shortlist.jd_id
    ).group_by(
        JobDescription.job_title
    ).order_by(
        text('shortlist_count DESC')
    ).limit(5).all()
    
    stats['top_shortlisted'] = [{'title': title, 'count': count} for title, count in top_shortlisted]
    
    return render_template('analytics/reports/dashboard.html', stats=stats)

@bp.route('/job-funnel')
def job_funnel():
    """Show the recruitment funnel for a specific job"""
    logger.debug("Loading job funnel report")
    
    job_id = request.args.get('job_id')
    
    if job_id:
        # Get specific job
        job = JobDescription.query.get_or_404(job_id)
        
        # Get funnel stats
        candidates_count = Candidate.query.count()
        matches_count = MatchScore.query.filter_by(jd_id=job_id).count()
        shortlisted_count = Shortlist.query.filter_by(jd_id=job_id).count()
        interview_count = db.session.query(Interview).join(
            Shortlist, Interview.shortlist_id == Shortlist.shortlist_id
        ).filter(
            Shortlist.jd_id == job_id
        ).count()
        hired_count = Shortlist.query.filter_by(jd_id=job_id, status='hired').count()
        
        # Calculate conversion rates
        match_rate = (matches_count / candidates_count) * 100 if candidates_count > 0 else 0
        shortlist_rate = (shortlisted_count / matches_count) * 100 if matches_count > 0 else 0
        interview_rate = (interview_count / shortlisted_count) * 100 if shortlisted_count > 0 else 0
        hire_rate = (hired_count / interview_count) * 100 if interview_count > 0 else 0
        
        funnel = {
            'candidates': candidates_count,
            'matches': matches_count,
            'shortlisted': shortlisted_count,
            'interviewed': interview_count,
            'hired': hired_count,
            'match_rate': round(match_rate, 1),
            'shortlist_rate': round(shortlist_rate, 1),
            'interview_rate': round(interview_rate, 1),
            'hire_rate': round(hire_rate, 1)
        }
        
        return render_template('analytics/reports/job_funnel.html', 
                              job=job,
                              funnel=funnel)
    else:
        # Get all jobs
        jobs = JobDescription.query.all()
        return render_template('analytics/reports/job_funnel_select.html', jobs=jobs)

@bp.route('/match-quality')
def match_quality():
    """Show match quality metrics"""
    logger.debug("Loading match quality report")
    
    # Get average scores by job
    job_scores = db.session.query(
        JobDescription.job_title,
        func.avg(MatchScore.overall_score).label('avg_score'),
        func.avg(MatchScore.skills_score).label('avg_skills'),
        func.avg(MatchScore.experience_score).label('avg_experience'),
        func.avg(MatchScore.education_score).label('avg_education'),
        func.count(MatchScore.match_id).label('match_count')
    ).join(
        MatchScore, 
        JobDescription.jd_id == MatchScore.jd_id
    ).group_by(
        JobDescription.job_title
    ).having(
        func.count(MatchScore.match_id) > 0
    ).order_by(
        text('avg_score DESC')
    ).all()
    
    formatted_scores = []
    for job in job_scores:
        formatted_scores.append({
            'job_title': job.job_title,
            'avg_score': round(job.avg_score, 1),
            'avg_skills': round(job.avg_skills, 1),
            'avg_experience': round(job.avg_experience, 1),
            'avg_education': round(job.avg_education, 1),
            'match_count': job.match_count
        })
    
    # Get score distribution
    score_distribution = db.session.query(
        func.floor(MatchScore.overall_score / 10) * 10,
        func.count(MatchScore.match_id)
    ).group_by(
        func.floor(MatchScore.overall_score / 10) * 10
    ).order_by(
        func.floor(MatchScore.overall_score / 10) * 10
    ).all()
    
    score_ranges = []
    for score_range, count in score_distribution:
        score_ranges.append({
            'range': f"{int(score_range)}-{int(score_range)+9}",
            'count': count
        })
    
    return render_template('analytics/reports/match_quality.html',
                          job_scores=formatted_scores,
                          score_distribution=score_ranges)

@bp.route('/time-to-hire')
def time_to_hire():
    """Show time-to-hire metrics"""
    logger.debug("Loading time-to-hire report")
    
    # Get shortlists with hired status
    hired_candidates = db.session.query(
        JobDescription.job_title,
        Shortlist.created_at.label('shortlist_date'),
        func.min(Interview.scheduled_date).label('first_interview'),
        func.max(Interview.scheduled_date).label('last_interview'),
        Shortlist.status,
    ).join(
        JobDescription,
        Shortlist.jd_id == JobDescription.jd_id
    ).join(
        Interview,
        Shortlist.shortlist_id == Interview.shortlist_id
    ).filter(
        Shortlist.status == 'hired'
    ).group_by(
        JobDescription.job_title,
        Shortlist.shortlist_id,
        Shortlist.created_at,
        Shortlist.status
    ).all()
    
    # Calculate time to hire
    time_to_hire_data = []
    for hire in hired_candidates:
        # Time from shortlist to first interview
        time_to_interview = (hire.first_interview - hire.shortlist_date).days
        
        # Time from first interview to last interview
        interview_process = (hire.last_interview - hire.first_interview).days if hire.last_interview != hire.first_interview else 0
        
        # Total time
        total_time = (hire.last_interview - hire.shortlist_date).days
        
        time_to_hire_data.append({
            'job_title': hire.job_title,
            'shortlist_date': hire.shortlist_date.strftime('%Y-%m-%d'),
            'first_interview': hire.first_interview.strftime('%Y-%m-%d'),
            'last_interview': hire.last_interview.strftime('%Y-%m-%d'),
            'time_to_interview': time_to_interview,
            'interview_process': interview_process,
            'total_time': total_time
        })
    
    # Calculate averages
    avg_time_to_interview = sum(item['time_to_interview'] for item in time_to_hire_data) / len(time_to_hire_data) if time_to_hire_data else 0
    avg_interview_process = sum(item['interview_process'] for item in time_to_hire_data) / len(time_to_hire_data) if time_to_hire_data else 0
    avg_total_time = sum(item['total_time'] for item in time_to_hire_data) / len(time_to_hire_data) if time_to_hire_data else 0
    
    averages = {
        'avg_time_to_interview': round(avg_time_to_interview, 1),
        'avg_interview_process': round(avg_interview_process, 1),
        'avg_total_time': round(avg_total_time, 1)
    }
    
    return render_template('analytics/reports/time_to_hire.html',
                          time_to_hire_data=time_to_hire_data,
                          averages=averages)

@bp.route('/api/dashboard-data')
def dashboard_data():
    """API endpoint to get dashboard data for charts"""
    # Get job funnel summary
    candidates_count = Candidate.query.count()
    matches_count = MatchScore.query.count()
    shortlisted_count = Shortlist.query.count()
    interview_count = Interview.query.count()
    hired_count = Shortlist.query.filter_by(status='hired').count()
    
    funnel = {
        'candidates': candidates_count,
        'matches': matches_count,
        'shortlisted': shortlisted_count,
        'interviewed': interview_count,
        'hired': hired_count
    }
    
    # Get match score distribution
    score_distribution = db.session.query(
        func.floor(MatchScore.overall_score / 10) * 10,
        func.count(MatchScore.match_id)
    ).group_by(
        func.floor(MatchScore.overall_score / 10) * 10
    ).order_by(
        func.floor(MatchScore.overall_score / 10) * 10
    ).all()
    
    score_ranges = {}
    for score_range, count in score_distribution:
        score_ranges[f"{int(score_range)}-{int(score_range)+9}"] = count
    
    # Get monthly hiring data for the past year
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=365)
    
    monthly_data = db.session.query(
        func.date_trunc('month', Shortlist.created_at).label('month'),
        func.count(Shortlist.shortlist_id).label('count')
    ).filter(
        Shortlist.created_at >= start_date,
        Shortlist.created_at <= end_date,
        Shortlist.status == 'hired'
    ).group_by(
        text('month')
    ).order_by(
        text('month')
    ).all()
    
    monthly_hiring = {}
    for month, count in monthly_data:
        monthly_hiring[month.strftime('%Y-%m')] = count
    
    return jsonify({
        'funnel': funnel,
        'score_distribution': score_ranges,
        'monthly_hiring': monthly_hiring
    })

# Register blueprint with the application
def init_app(app):
    app.register_blueprint(bp)
    
    # Also register the routes directly with the app for compatibility
    app.add_url_rule('/analytics/reports/', view_func=reports_dashboard)
    app.add_url_rule('/analytics/reports/job-funnel', view_func=job_funnel)
    app.add_url_rule('/analytics/reports/match-quality', view_func=match_quality)
    app.add_url_rule('/analytics/reports/time-to-hire', view_func=time_to_hire)
    app.add_url_rule('/analytics/reports/api/dashboard-data', view_func=dashboard_data)