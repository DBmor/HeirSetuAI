# app/models/notification.py
from app.extensions import db
from datetime import datetime


class Notification(db.Model):
    """System and feature notifications model"""
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), default="info")  # info, warning, application_update, background_check
    is_read = db.Column(db.Boolean, default=False)
    link = db.Column(db.String(255), nullable=True)  # URL or action link

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    user = db.relationship("User", backref="notifications")

    def __repr__(self):
        return f"<Notification {self.id} for User {self.user_id}>"
