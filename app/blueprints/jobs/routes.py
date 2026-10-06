# app/blueprints/jobs/routes.py
from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.job import Job
from app.models.user import User, RoleEnum

jobs_bp = Blueprint("jobs", __name__, url_prefix="/jobs")


@jobs_bp.route("", methods=["GET"])
def list_jobs():
    """Get active job listings"""
    search = request.args.get("search", "")
    location = request.args.get("location", "")

    query = Job.query.filter_by(status="active")
    if search:
        query = query.filter(Job.title.ilike(f"%{search}%"))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))

    jobs = query.order_by(Job.created_at.desc()).all()
    
    if request.is_json:
        return jsonify([{
            "id": j.id,
            "title": j.title,
            "company_id": j.company_id,
            "location": j.location,
            "job_type": j.job_type,
            "salary_range": j.salary_range,
            "created_at": j.created_at.isoformat()
        } for j in jobs]), 200

    return render_template("candidate/job_search.html", jobs=jobs)


@jobs_bp.route("/<int:job_id>", methods=["GET"])
def job_detail(job_id):
    """View job detail"""
    job = Job.query.get_or_404(job_id)
    
    if request.is_json:
        return jsonify({
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "requirements": job.requirements,
            "location": job.location,
            "job_type": job.job_type,
            "salary_range": job.salary_range,
            "skills_required": job.skills_required or []
        }), 200

    return render_template("candidate/job_detail.html", job=job)


@jobs_bp.route("/create", methods=["POST"])
@jwt_required()
def create_job():
    """Create a new job posting (company role required)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != RoleEnum.company:
        return jsonify({"message": "Access denied"}), 403

    data = request.get_json() or request.form.to_dict()
    title = data.get("title")
    description = data.get("description")

    if not title or not description:
        return jsonify({"message": "Title and description are required"}), 400

    job = Job(
        company_id=user_id,
        title=title,
        description=description,
        requirements=data.get("requirements"),
        location=data.get("location"),
        job_type=data.get("job_type", "Full-time"),
        salary_range=data.get("salary_range"),
        skills_required=data.get("skills", []),
        status="active"
    )
    db.session.add(job)
    db.session.commit()

    return jsonify({"message": "Job created successfully", "job_id": job.id}), 201
