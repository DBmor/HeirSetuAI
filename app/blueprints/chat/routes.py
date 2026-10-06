# app/blueprints/chat/routes.py
from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.chat import Chat
from app.models.user import User

chat_bp = Blueprint("chat", __name__, url_prefix="/chat")


@chat_bp.route("/messages/<int:other_user_id>", methods=["GET"])
@jwt_required()
def get_messages(other_user_id):
    """Get chat history with another user"""
    user_id = get_jwt_identity()

    chats = Chat.query.filter(
        ((Chat.sender_id == user_id) & (Chat.receiver_id == other_user_id)) |
        ((Chat.sender_id == other_user_id) & (Chat.receiver_id == user_id))
    ).order_by(Chat.created_at.asc()).all()

    return jsonify([{
        "id": c.id,
        "sender_id": c.sender_id,
        "receiver_id": c.receiver_id,
        "message": c.message,
        "is_read": c.is_read,
        "created_at": c.created_at.isoformat()
    } for c in chats]), 200


@chat_bp.route("/send", methods=["POST"])
@jwt_required()
def send_message():
    """Send a direct message"""
    user_id = get_jwt_identity()
    data = request.get_json() or request.form.to_dict()

    receiver_id = data.get("receiver_id")
    message = data.get("message")

    if not receiver_id or not message:
        return jsonify({"message": "receiver_id and message are required"}), 400

    chat = Chat(
        sender_id=user_id,
        receiver_id=receiver_id,
        message=message
    )
    db.session.add(chat)
    db.session.commit()

    return jsonify({"message": "Message sent", "chat_id": chat.id}), 201
