# app/models/chat.py
from app.extensions import db
from datetime import datetime


class Chat(db.Model):
    """Chat message model between candidates and company recruiters"""
    __tablename__ = "chats"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    message = db.Column(db.Text, nullable=False)
    file_path = db.Column(db.String(500), nullable=True)  # Optional attached file/image
    is_read = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    sender = db.relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    receiver = db.relationship("User", foreign_keys=[receiver_id], backref="received_messages")

    def __repr__(self):
        return f"<Chat {self.id}: {self.sender_id} -> {self.receiver_id}>"
