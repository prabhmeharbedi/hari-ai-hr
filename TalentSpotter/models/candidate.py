from datetime import datetime
from database import db

class Candidate(db.Model):
    __tablename__ = "candidates"

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    resume_text = db.Column(db.Text)
    resume_file_path = db.Column(db.String(255))
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    shortlist_entries = db.relationship("ShortlistCandidate", back_populates="candidate", cascade="all, delete-orphan")
    match_scores = db.relationship("MatchScore", back_populates="candidate", cascade="all, delete-orphan")
    interviews = db.relationship("Interview", back_populates="candidate", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Candidate {self.name}>' 