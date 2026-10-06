# app/models/resume.py
from app.extensions import db
from datetime import datetime


class Resume(db.Model):
    """Candidate resume/CV storage"""
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    
    # File information
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)  # Relative path to uploaded file
    file_size = db.Column(db.Integer, nullable=True)  # In bytes
    
    # Resume details
    title = db.Column(db.String(255), nullable=True)  # E.g., "Senior Developer Resume"
    is_primary = db.Column(db.Boolean, default=False)  # Only one primary resume per user
    
    # Parsing & Analysis
    parsed_data = db.Column(db.JSON, nullable=True)  # Structured resume data from parser
    skills = db.Column(db.JSON, nullable=True)  # List of extracted skills
    experience_years = db.Column(db.Float, nullable=True)  # Total years of experience
    
    # Scanning results (from Resume Scanner Agent)
    scan_status = db.Column(db.String(50), default="pending")  # pending / scanning / completed / failed
    match_score = db.Column(db.Float, nullable=True)  # Overall match score (0-100)
    missing_keywords = db.Column(db.JSON, nullable=True)  # Keywords missing from job requirement
    scan_results = db.Column(db.JSON, nullable=True)  # Detailed scan results
    
    # Metadata
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='resumes')
    
    def __repr__(self):
        return f"<Resume {self.filename} - User {self.user_id}>"
