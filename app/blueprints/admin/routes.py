# app/blueprints/admin/routes.py
from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User, RoleEnum, CompanyProfile

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/companies/pending", methods=["GET"])
@jwt_required()
def pending_companies():
    """Get list of companies awaiting verification"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != RoleEnum.admin:
        return jsonify({"message": "Admin access required"}), 403

    pending = CompanyProfile.query.filter_by(status="verification_in_progress").all()
    return jsonify([{
        "id": c.id,
        "company_name": c.company_legal_name,
        "application_id": c.application_id,
        "official_email": c.official_email,
        "website": c.website,
        "submitted_at": c.submitted_at.isoformat() if c.submitted_at else None
    } for c in pending]), 200
