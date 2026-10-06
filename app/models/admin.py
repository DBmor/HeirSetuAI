# app/models/admin.py
from app.extensions import db
from datetime import datetime


class Admin(db.Model):
    """Admin profile model"""
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    
    department = db.Column(db.String(100), nullable=True)
    permissions = db.Column(db.JSON, nullable=True)  # List of permissions or roles
    is_superadmin = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = db.relationship("User", backref=db.backref("admin_profile", uselist=False))

    def __repr__(self):
        return f"<Admin User {self.user_id}>"
