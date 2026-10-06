# app/blueprints/candidate/routes.py
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from datetime import datetime

from app.extensions import db
from app.models.user import User, RoleEnum, CandidateProfile
from app.models.resume import Resume
from app.blueprints.candidate.forms import (
    CandidateProfileForm,
    ResumeUploadForm,
    CandidateSkillsForm,
    JobPreferencesForm
)
from app.utils.file_storage import save_upload_file

candidate_bp = Blueprint("candidate", __name__, url_prefix="/candidate")


# ========== HELPERS ==========
def get_or_create_candidate_profile(user_id):
    """Get candidate profile or create if doesn't exist"""
    profile = CandidateProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = CandidateProfile(user_id=user_id)
        db.session.add(profile)
        db.session.commit()
    return profile


# ========== HOME / DASHBOARD ==========
@candidate_bp.route("/home", methods=["GET"])
@jwt_required()
def home():
    """Candidate dashboard - shows welcome and quick actions"""
    raw_id = get_jwt_identity()
    user_id = int(raw_id) if raw_id else None
    user = User.query.get(user_id) if user_id else None
    
    role_str = user.role.value if user and hasattr(user.role, "value") else str(user.role if user else "")
    if not user or role_str != "candidate":
        return jsonify({"message": "Access denied"}), 403
    
    # Get or create candidate profile
    profile = get_or_create_candidate_profile(user_id)
    
    # Get resume count
    resume_count = Resume.query.filter_by(user_id=user_id).count()
    primary_resume = Resume.query.filter_by(user_id=user_id, is_primary=True).first() if resume_count > 0 else None
    
    # Calculate profile completion
    profile_fields = [
        profile.phone,
        profile.location,
        profile.headline,
        profile.bio,
        profile.current_title,
        profile.current_company,
        profile.linkedin_url,
        profile.github_url,
    ]
    completed_fields = sum(1 for field in profile_fields if field)
    profile_completion = (completed_fields / len(profile_fields) * 100) if profile_fields else 0
    profile.profile_completion = int(profile_completion)
    db.session.commit()
    
    return render_template(
        "candidate/home.html",
        user=user,
        profile=profile,
        resume_count=resume_count,
        primary_resume=primary_resume,
        profile_completion=int(profile_completion)
    )


# ========== PROFILE ==========
@candidate_bp.route("/profile", methods=["GET"])
@jwt_required()
def view_profile():
    """View candidate profile"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role != RoleEnum.candidate:
        return jsonify({"message": "Access denied"}), 403
    
    profile = get_or_create_candidate_profile(user_id)
    resumes = Resume.query.filter_by(user_id=user_id).order_by(Resume.uploaded_at.desc()).all()
    
    return render_template(
        "candidate/profile.html",
        user=user,
        profile=profile,
        resumes=resumes
    )


@candidate_bp.route("/profile/edit", methods=["GET", "POST"])
@jwt_required()
def edit_profile():
    """Edit candidate profile"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role != RoleEnum.candidate:
        return jsonify({"message": "Access denied"}), 403
    
    profile = get_or_create_candidate_profile(user_id)
    form = CandidateProfileForm()
    
    if form.validate_on_submit():
        try:
            # Update profile fields
            profile.phone = form.phone.data
            profile.location = form.location.data
            profile.headline = form.headline.data
            profile.bio = form.bio.data
            profile.experience_level = form.experience_level.data
            profile.total_experience_years = form.total_experience_years.data
            profile.current_title = form.current_title.data
            profile.current_company = form.current_company.data
            profile.linkedin_url = form.linkedin_url.data
            profile.github_url = form.github_url.data
            profile.portfolio_url = form.portfolio_url.data
            profile.is_open_to_work = form.is_open_to_work.data
            profile.visibility = form.visibility.data
            
            db.session.commit()
            
            if request.is_json:
                return jsonify({
                    "success": True,
                    "message": "Profile updated successfully"
                }), 200
            else:
                flash("Profile updated successfully!", "success")
                return redirect(url_for("candidate.view_profile"))
        
        except Exception as e:
            db.session.rollback()
            error_msg = f"Error updating profile: {str(e)}"
            if request.is_json:
                return jsonify({"success": False, "message": error_msg}), 500
            else:
                flash(error_msg, "error")
    
    # Populate form with existing data
    if request.method == "GET":
        form.phone.data = profile.phone
        form.location.data = profile.location
        form.headline.data = profile.headline
        form.bio.data = profile.bio
        form.experience_level.data = profile.experience_level
        form.total_experience_years.data = profile.total_experience_years
        form.current_title.data = profile.current_title
        form.current_company.data = profile.current_company
        form.linkedin_url.data = profile.linkedin_url
        form.github_url.data = profile.github_url
        form.portfolio_url.data = profile.portfolio_url
        form.is_open_to_work.data = profile.is_open_to_work
        form.visibility.data = profile.visibility
    
    return render_template(
        "candidate/edit_profile.html",
        user=user,
        profile=profile,
        form=form
    )


# ========== RESUME UPLOAD ==========
@candidate_bp.route("/resume/upload", methods=["GET", "POST"])
@jwt_required()
def upload_resume():
    """Upload a new resume"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role != RoleEnum.candidate:
        return jsonify({"message": "Access denied"}), 403
    
    profile = get_or_create_candidate_profile(user_id)
    form = ResumeUploadForm()
    
    if form.validate_on_submit():
        try:
            if not form.resume_file.data:
                return jsonify({"success": False, "message": "No file selected"}), 400
            
            # Get current resume count before adding new one
            resume_count = Resume.query.filter_by(user_id=user_id).count()
            
            # Save file
            file_obj = form.resume_file.data
            filename = secure_filename(file_obj.filename)
            file_path = save_upload_file(
                file_obj,
                category="resumes",
                user_id=user_id
            )
            
            # If this is set as primary, unset other primary resumes
            if form.is_primary.data:
                Resume.query.filter_by(user_id=user_id, is_primary=True).update({"is_primary": False})
            
            # Create resume record
            resume = Resume(
                user_id=user_id,
                filename=filename,
                file_path=file_path,
                file_size=len(file_obj.read()),
                title=form.title.data or filename,
                is_primary=form.is_primary.data or resume_count == 0  # First resume is primary
            )
            
            # Update candidate profile resume count
            profile.resume_count = resume_count + 1
            
            db.session.add(resume)
            db.session.commit()
            
            if request.is_json:
                return jsonify({
                    "success": True,
                    "message": "Resume uploaded successfully",
                    "resume_id": resume.id
                }), 201
            else:
                flash(f"Resume '{filename}' uploaded successfully!", "success")
                return redirect(url_for("candidate.view_resumes"))
        
        except Exception as e:
            db.session.rollback()
            error_msg = f"Error uploading resume: {str(e)}"
            if request.is_json:
                return jsonify({"success": False, "message": error_msg}), 500
            else:
                flash(error_msg, "error")
    
    elif form.errors and request.is_json:
        return jsonify({"success": False, "errors": form.errors}), 400
    
    return render_template(
        "candidate/resume_upload.html",
        user=user,
        form=form
    )


# ========== RESUME MANAGEMENT ==========
@candidate_bp.route("/resumes", methods=["GET"])
@jwt_required()
def view_resumes():
    """View all resumes"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role != RoleEnum.candidate:
        return jsonify({"message": "Access denied"}), 403
    
    resumes = Resume.query.filter_by(user_id=user_id).order_by(Resume.uploaded_at.desc()).all()
    
    return render_template(
        "candidate/resumes.html",
        user=user,
        resumes=resumes
    )


@candidate_bp.route("/resume/<int:resume_id>/set-primary", methods=["POST"])
@jwt_required()
def set_primary_resume(resume_id):
    """Set resume as primary"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role != RoleEnum.candidate:
        return jsonify({"message": "Access denied"}), 403
    
    resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
    if not resume:
        return jsonify({"message": "Resume not found"}), 404
    
    try:
        # Unset other primary resumes
        Resume.query.filter_by(user_id=user_id, is_primary=True).update({"is_primary": False})
        resume.is_primary = True
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"'{resume.title}' is now your primary resume"
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error updating resume: {str(e)}"
        }), 500


@candidate_bp.route("/resume/<int:resume_id>/delete", methods=["POST"])
@jwt_required()
def delete_resume(resume_id):
    """Delete a resume"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role != RoleEnum.candidate:
        return jsonify({"message": "Access denied"}), 403
    
    resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
    if not resume:
        return jsonify({"message": "Resume not found"}), 404
    
    try:
        # Delete file
        from app.utils.file_storage import delete_file
        delete_file(resume.file_path)
        
        # Delete database record
        db.session.delete(resume)
        
        # Update profile resume count
        profile = get_or_create_candidate_profile(user_id)
        profile.resume_count = Resume.query.filter_by(user_id=user_id).count() - 1
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Resume deleted successfully"
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error deleting resume: {str(e)}"
        }), 500


# ========== API ENDPOINTS ==========
@candidate_bp.route("/api/profile", methods=["GET"])
@jwt_required()
def api_get_profile():
    """Get candidate profile as JSON"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role != RoleEnum.candidate:
        return jsonify({"message": "Access denied"}), 403
    
    profile = get_or_create_candidate_profile(user_id)
    
    return jsonify({
        "name": user.name,
        "email": user.email,
        "phone": profile.phone,
        "location": profile.location,
        "headline": profile.headline,
        "bio": profile.bio,
        "current_title": profile.current_title,
        "current_company": profile.current_company,
        "experience_level": profile.experience_level,
        "total_experience_years": profile.total_experience_years,
        "skills": profile.skills or [],
        "languages": profile.languages or [],
        "linkedin_url": profile.linkedin_url,
        "github_url": profile.github_url,
        "portfolio_url": profile.portfolio_url,
        "is_open_to_work": profile.is_open_to_work,
        "profile_completion": profile.profile_completion,
        "created_at": user.created_at.isoformat()
    }), 200
