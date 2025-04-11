"""
Routes for shortlist management
"""
import logging
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Shortlist, ShortlistCandidate, Job, Candidate
from database import db
from database.db_operations import serialize_json_fields, prepare_for_storage
from datetime import datetime

logger = logging.getLogger(__name__)

# Create blueprint
bp = Blueprint('shortlists', __name__, url_prefix='/shortlists')

@bp.route('/')
def index():
    shortlists = Shortlist.query.join(Job).all()
    return render_template('shortlists/index.html', shortlists=shortlists)

@bp.route('/new', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        job_id = request.form.get('job_id')
        notes = request.form.get('notes')
        
        shortlist = Shortlist(
            name=name,
            job_id=job_id,
            notes=notes,
            status='active',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(shortlist)
        db.session.commit()
        
        flash('Shortlist created successfully', 'success')
        return redirect(url_for('shortlists.view', id=shortlist.id))
        
    jobs = Job.query.all()
    return render_template('shortlists/new.html', jobs=jobs)

@bp.route('/<int:id>')
def view(id):
    shortlist = Shortlist.query.get_or_404(id)
    candidates = ShortlistCandidate.query.filter_by(shortlist_id=id, status='active').all()
    return render_template('shortlists/view.html', shortlist=shortlist, candidates=candidates)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    shortlist = Shortlist.query.get_or_404(id)
    
    if request.method == 'POST':
        shortlist.name = request.form.get('name')
        shortlist.job_id = request.form.get('job_id')
        shortlist.notes = request.form.get('notes')
        shortlist.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Shortlist updated successfully', 'success')
        return redirect(url_for('shortlists.view', id=id))
        
    jobs = Job.query.all()
    return render_template('shortlists/edit.html', shortlist=shortlist, jobs=jobs)

@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    shortlist = Shortlist.query.get_or_404(id)
    shortlist.status = 'deleted'
    shortlist.updated_at = datetime.utcnow()
    
    db.session.commit()
    flash('Shortlist deleted successfully', 'success')
    return redirect(url_for('shortlists.index'))

@bp.route('/<int:id>/add_candidate', methods=['POST'])
def add_candidate(id):
    shortlist = Shortlist.query.get_or_404(id)
    candidate_id = request.form.get('candidate_id')
    
    # Check if candidate already exists in shortlist
    existing = ShortlistCandidate.query.filter_by(
        shortlist_id=id,
        candidate_id=candidate_id,
        status='active'
    ).first()
    
    if existing:
        flash('Candidate already in shortlist', 'error')
        return redirect(url_for('shortlists.view', id=id))
        
    shortlist_candidate = ShortlistCandidate(
        shortlist_id=id,
        candidate_id=candidate_id,
        status='active',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.session.add(shortlist_candidate)
    db.session.commit()
    
    flash('Candidate added to shortlist', 'success')
    return redirect(url_for('shortlists.view', id=id))

@bp.route('/<int:id>/remove_candidate/<int:candidate_id>', methods=['POST'])
def remove_candidate(id, candidate_id):
    shortlist_candidate = ShortlistCandidate.query.filter_by(
        shortlist_id=id,
        candidate_id=candidate_id,
        status='active'
    ).first_or_404()
    
    shortlist_candidate.status = 'removed'
    shortlist_candidate.updated_at = datetime.utcnow()
    
    db.session.commit()
    flash('Candidate removed from shortlist', 'success')
    return redirect(url_for('shortlists.view', id=id))

def init_app(app):
    """Initialize the shortlists blueprint with the app"""
    app.register_blueprint(bp) 