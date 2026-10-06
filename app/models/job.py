# app/models/job.py
from app.extensions import db
from datetime import datetime


class Job(db.Model):
    """Job listing model"""
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(255), nullable=True)
    job_type = db.Column(db.String(50), nullable=True)  # Full-time, Part-time, Contract, Remote
    salary_range = db.Column(db.String(100), nullable=True)
    experience_required = db.Column(db.String(50), nullable=True)
    skills_required = db.Column(db.JSON, nullable=True)  # List of skills: ["Python", "Flask", ...]

    status = db.Column(db.String(50), default="active", nullable=False)  # active, closed, draft

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = db.relationship("User", backref="jobs")
    applications = db.relationship("Application", backref="job", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Job {self.title} - Company {self.company_id}>"
