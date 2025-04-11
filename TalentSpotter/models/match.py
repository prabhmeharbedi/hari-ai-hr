from datetime import datetime
from database import db

class MatchScore(db.Model):
    __tablename__ = 'match_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    overall_score = db.Column(db.Float, nullable=False)
    skills_score = db.Column(db.Float, nullable=False)
    experience_score = db.Column(db.Float, nullable=False)
    education_score = db.Column(db.Float, nullable=False)
    certifications_score = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    job = db.relationship('Job', back_populates="match_scores")
    candidate = db.relationship('Candidate', back_populates="match_scores")
    
    def __repr__(self):
        return f'<MatchScore {self.job_id}-{self.candidate_id}: {self.overall_score}>' 