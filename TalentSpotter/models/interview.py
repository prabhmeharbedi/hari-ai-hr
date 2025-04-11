from datetime import datetime
from database import db

class Interview(db.Model):
    __tablename__ = "interviews"
    
    id = db.Column(db.Integer, primary_key=True)
    shortlist_id = db.Column(db.Integer, db.ForeignKey('shortlists.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    scheduled_date = db.Column(db.DateTime)
    format = db.Column(db.String(50))  # in-person, video, phone
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    notes = db.Column(db.Text)
    feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    shortlist = db.relationship("Shortlist", back_populates="interviews")
    candidate = db.relationship("Candidate", back_populates="interviews")
    job = db.relationship("Job", back_populates="interviews")
    
    def __repr__(self):
        return f'<Interview {self.id}: {self.shortlist_id}>' 