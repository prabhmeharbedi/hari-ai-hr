from datetime import datetime
from database import db

class ShortlistCandidate(db.Model):
    """Model for shortlist candidates"""
    __tablename__ = 'shortlist_candidates'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    shortlist_id = db.Column(db.Integer, db.ForeignKey('shortlists.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    shortlist = db.relationship("Shortlist", back_populates="shortlist_candidates")
    candidate = db.relationship("Candidate", back_populates="shortlist_entries")
    
    def __repr__(self):
        return f'<ShortlistCandidate shortlist_id={self.shortlist_id} candidate_id={self.candidate_id}>' 