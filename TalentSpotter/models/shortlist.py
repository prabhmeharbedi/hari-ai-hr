from datetime import datetime
from database import db

class Shortlist(db.Model):
    __tablename__ = "shortlists"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')  # active, archived
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    job = db.relationship("Job", back_populates="shortlists")
    shortlist_candidates = db.relationship("ShortlistCandidate", back_populates="shortlist", cascade="all, delete-orphan")
    interviews = db.relationship("Interview", back_populates="shortlist", cascade="all, delete-orphan")

    @property
    def candidate_count(self):
        return len([sc for sc in self.shortlist_candidates if sc.status == 'active'])

    def __repr__(self):
        return f'<Shortlist {self.name}>' 