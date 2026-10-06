from app.extensions import db
from datetime import datetime


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)

    # Candidate who applied
    candidate_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    # Job being applied for
    job_id = db.Column(
        db.Integer,
        db.ForeignKey("jobs.id"),
        nullable=False
    )

    # Application status
    status = db.Column(
        db.String(50),
        default="Applied",
        nullable=False
    )

    # Optional cover letter
    cover_letter = db.Column(
        db.Text,
        nullable=True
    )

    # Date of application
    applied_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<Application {self.id}>"