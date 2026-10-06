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
    candidate_profile = db.relationship(
        "CandidateProfile", backref="user", uselist=False, cascade="all, delete-orphan"
    )


class CompanyProfile(db.Model):
    """Company-only fields, linked 1:1 to a User with role=company."""
    __tablename__ = "company_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)

    # === Registration Step 1: Representative Info ===
    representative_name = db.Column(db.String(150), nullable=True)
    designation = db.Column(db.String(100), nullable=True)
    official_email = db.Column(db.String(150), nullable=True)
    email_otp_verified = db.Column(db.Boolean, default=False)
    phone = db.Column(db.String(20), nullable=True)
    phone_otp_verified = db.Column(db.Boolean, default=False)
    linkedin_profile = db.Column(db.String(255), nullable=True)
    government_id_path = db.Column(db.String(255), nullable=True)  # file path
    authorization_letter_path = db.Column(db.String(255), nullable=True)  # file path

    # === Registration Step 2: Company Details ===
    company_legal_name = db.Column(db.String(255), nullable=True)
    corporate_id = db.Column(db.String(50), nullable=True)  # CIN/GST/PAN
    business_type = db.Column(db.String(50), nullable=True)
    incorporation_date = db.Column(db.Date, nullable=True)
    company_email = db.Column(db.String(150), nullable=True)
    company_phone = db.Column(db.String(20), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    registered_address = db.Column(db.Text, nullable=True)

    # === Registration Step 3: Documents ===
    incorporation_document_path = db.Column(db.String(255), nullable=True)
    tax_document_path = db.Column(db.String(255), nullable=True)
    license_document_path = db.Column(db.String(255), nullable=True)

    # === Registration Step 4: Security & Consent ===
    terms_accepted = db.Column(db.Boolean, default=False)
    privacy_accepted = db.Column(db.Boolean, default=False)

    # === Verification & Status ===
    application_id = db.Column(db.String(50), unique=True, nullable=True)  # HSR-YYYY-MM-XXXXX
    registration_step = db.Column(db.Integer, default=1)  # 1-5
    status = db.Column(db.String(20), default="pending")  # pending / verification_in_progress / approved / rejected / flagged
    legitimacy_score = db.Column(db.Integer, nullable=True)  # set by Agent 3
    rejection_reason = db.Column(db.Text, nullable=True)
    
    submitted_at = db.Column(db.DateTime, nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CandidateProfile(db.Model):
    """Candidate-only fields, linked 1:1 to a User with role=candidate."""
    __tablename__ = "candidate_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)

    # Basic Information
    phone = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    headline = db.Column(db.String(255), nullable=True)  # E.g., "Senior Full Stack Developer"
    
    # Professional Details
    experience_level = db.Column(db.String(50), nullable=True)  # entry / mid / senior / lead / executive
    total_experience_years = db.Column(db.Float, nullable=True)
    current_title = db.Column(db.String(150), nullable=True)
    current_company = db.Column(db.String(150), nullable=True)
    
    # Skills & Expertise
    skills = db.Column(db.JSON, nullable=True)  # List of skills: ["Python", "React", "AWS", ...]
    languages = db.Column(db.JSON, nullable=True)  # Languages spoken: ["English", "Hindi", ...]
    
    # Education
    education = db.Column(db.JSON, nullable=True)  # List of education records
    
    # Links & Social
    linkedin_url = db.Column(db.String(255), nullable=True)
    github_url = db.Column(db.String(255), nullable=True)
    portfolio_url = db.Column(db.String(255), nullable=True)
    
    # Resume Information
    primary_resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=True)
    resume_count = db.Column(db.Integer, default=0)  # Number of resumes uploaded
    
    # Job Preferences
    job_preferences = db.Column(db.JSON, nullable=True)  # Preferred roles, locations, job types
    preferred_job_types = db.Column(db.JSON, nullable=True)  # ["Full-time", "Part-time", "Contract", ...]
    preferred_locations = db.Column(db.JSON, nullable=True)  # ["Remote", "New York", ...]
    
    # Profile Status
    profile_completion = db.Column(db.Integer, default=0)  # 0-100% completion
    is_open_to_work = db.Column(db.Boolean, default=True)
    visibility = db.Column(db.String(20), default="public")  # public / private / companies_only
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
