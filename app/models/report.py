# app/models/report.py
from app.extensions import db
from datetime import datetime


class Report(db.Model):
    """AI Agent Report storage (Background check, Company legitimacy, Resume scan)"""
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    report_type = db.Column(db.String(50), nullable=False)  # background_check, fake_company, resume_scan
    target_id = db.Column(db.Integer, nullable=True)  # ID of subject entity (candidate, company, or job)
    score = db.Column(db.Float, nullable=True)  # Match score or trust score
    status = db.Column(db.String(50), default="completed")  # pending, completed, failed
    summary = db.Column(db.Text, nullable=True)
    details = db.Column(db.JSON, nullable=True)  # Detailed JSON payload from AI agent

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = db.relationship("User", backref="reports")

    def __repr__(self):
        return f"<Report {self.id} - Type {self.report_type}>"
