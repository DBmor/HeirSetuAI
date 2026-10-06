# app/blueprints/api/routes.py
from flask import Blueprint, jsonify

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")


@api_bp.route("/status", methods=["GET"])
def system_status():
    """Health check status endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "HeirSetuAI API",
        "version": "1.0.0"
    }), 200
