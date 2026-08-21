# app/models/user.py
from app.extensions import db
from datetime import datetime
import enum


class RoleEnum(enum.Enum):
    candidate = "candidate"
    company = "company"
    admin = "admin"


class User(db.Model):
    """
    One shared table for candidates AND companies.
    Role-specific fields live in CompanyProfile (1:1), keeping auth logic identical
    for both roles instead of writing two parallel login/register systems.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)          # full name OR company name
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)  # nullable: Google-only accounts have no password
    role = db.Column(db.Enum(RoleEnum), nullable=False, default=RoleEnum.candidate)

    google_id = db.Column(db.String(255), unique=True, nullable=True)
    is_verified = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    company_profile = db.relationship(
        "CompanyProfile", backref="user", uselist=False, cascade="all, delete-orphan"
    )


class CompanyProfile(db.Model):
    """Company-only fields, linked 1:1 to a User with role=company."""
    __tablename__ = "company_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)

    website = db.Column(db.String(255), nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(150), nullable=True)
    about = db.Column(db.Text, nullable=True)

    legitimacy_score = db.Column(db.Integer, nullable=True)   # set by Agent 3
    status = db.Column(db.String(20), default="pending")       # pending / approved / rejected / flagged
