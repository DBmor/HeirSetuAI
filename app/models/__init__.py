# app/models/__init__.py
from app.models.user import User, RoleEnum, CompanyProfile, CandidateProfile
from app.models.resume import Resume
from app.models.application import Application
from app.models.job import Job
from app.models.chat import Chat
from app.models.notification import Notification
from app.models.report import Report
from app.models.admin import Admin

__all__ = [
    'User',
    'RoleEnum',
    'CompanyProfile',
    'CandidateProfile',
    'Resume',
    'Application',
    'Job',
    'Chat',
    'Notification',
    'Report',
    'Admin',
]
