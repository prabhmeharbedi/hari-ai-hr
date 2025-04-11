from datetime import datetime
from database import db

class Job(db.Model):
    """Model for job postings"""
    __tablename__ = 'jobs'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    department = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    status = db.Column(db.Text, nullable=False, default='open')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    match_scores = db.relationship("MatchScore", back_populates="job", cascade="all, delete-orphan")
    shortlists = db.relationship("Shortlist", back_populates="job", cascade="all, delete-orphan")
    interviews = db.relationship("Interview", back_populates="job", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Job {self.title}>' 