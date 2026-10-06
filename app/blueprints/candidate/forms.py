# app/blueprints/candidate/forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, FloatField, URLField, BooleanField, TelField
from wtforms.validators import DataRequired, Email, Length, Optional, URL, ValidationError


class CandidateProfileForm(FlaskForm):
    """Candidate profile update form"""
    phone = TelField(
        'Phone number',
        validators=[Optional()]
    )
    location = StringField(
        'Location',
        validators=[Optional(), Length(max=255)]
    )
    headline = StringField(
        'Professional headline',
        validators=[Optional(), Length(max=255)],
        description="e.g., Senior Full Stack Developer"
    )
    bio = TextAreaField(
        'Bio',
        validators=[Optional(), Length(max=2000)],
        description="Tell us about yourself"
    )
    experience_level = SelectField(
        'Experience level',
        choices=[
            ('', 'Select experience level'),
            ('entry', 'Entry Level (0-2 years)'),
            ('mid', 'Mid Level (2-5 years)'),
            ('senior', 'Senior (5-10 years)'),
            ('lead', 'Lead/Manager'),
            ('executive', 'Executive'),
        ],
        validators=[Optional()]
    )
    total_experience_years = FloatField(
        'Total years of experience',
        validators=[Optional()]
    )
    current_title = StringField(
        'Current job title',
        validators=[Optional(), Length(max=150)]
    )
    current_company = StringField(
        'Current company',
        validators=[Optional(), Length(max=150)]
    )
    linkedin_url = URLField(
        'LinkedIn profile URL',
        validators=[Optional()]
    )
    github_url = URLField(
        'GitHub profile URL',
        validators=[Optional()]
    )
    portfolio_url = URLField(
        'Portfolio website',
        validators=[Optional()]
    )
    is_open_to_work = BooleanField(
        'I am open to work opportunities',
        default=True
    )
    visibility = SelectField(
        'Profile visibility',
        choices=[
            ('public', 'Public - Anyone can view'),
            ('companies_only', 'Companies Only'),
            ('private', 'Private - Not searchable'),
        ],
        default='public'
    )


class ResumeUploadForm(FlaskForm):
    """Form for uploading resume/CV"""
    resume_file = FileField(
        'Upload Resume',
        validators=[
            DataRequired(),
            FileAllowed(['pdf', 'doc', 'docx', 'txt'], 'PDF, DOC, DOCX, or TXT files only')
        ]
    )
    title = StringField(
        'Resume title (optional)',
        validators=[Optional(), Length(max=255)],
        description="e.g., 'Latest Resume 2024'"
    )
    is_primary = BooleanField(
        'Set as primary resume for applications',
        default=False
    )


class CandidateSkillsForm(FlaskForm):
    """Form for adding/updating skills"""
    skills_input = StringField(
        'Skills (comma-separated)',
        validators=[DataRequired(), Length(min=2, max=1000)],
        description="e.g., Python, React, AWS, Machine Learning"
    )
    languages_input = StringField(
        'Languages (comma-separated)',
        validators=[Optional(), Length(max=500)],
        description="e.g., English, Hindi, Spanish"
    )


class JobPreferencesForm(FlaskForm):
    """Form for updating job preferences"""
    preferred_job_types = StringField(
        'Preferred job types (comma-separated)',
        validators=[Optional()],
        description="e.g., Full-time, Part-time, Remote"
    )
    preferred_locations = StringField(
        'Preferred job locations (comma-separated)',
        validators=[Optional()],
        description="e.g., San Francisco, Remote, New York"
    )
