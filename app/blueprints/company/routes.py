# app/blueprints/company/routes.py
from flask import Blueprint, request, jsonify, render_template, session, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import random
import string
from datetime import datetime, timedelta

from app.extensions import db
from app.models.user import User, CompanyProfile, RoleEnum
from app.blueprints.auth.forms import (
    CompanyRegistrationStep1Form, 
    CompanyRegistrationStep2Form,
    CompanyRegistrationStep3Form,
    CompanyRegistrationStep4Form
)
from app.utils.email_utils import send_otp_email
from app.utils.file_storage import save_upload_file

company_bp = Blueprint("company", __name__, url_prefix="/company")

# ========== HELPERS ==========
def generate_otp(length=6):
    """Generate random OTP"""
    return ''.join(random.choices(string.digits, k=length))


def generate_application_id():
    """Generate unique application ID like HSR-2026-09-000001"""
    timestamp = datetime.utcnow()
    year = timestamp.year
    month = timestamp.month
    # Find next sequential number for this month
    count = CompanyProfile.query.filter(
        db.func.strftime('%Y-%m', CompanyProfile.created_at) == f"{year}-{month:02d}"
    ).count() + 1
    return f"HSR-{year}-{month:02d}-{count:06d}"


def get_session_key(user_id, step):
    """Get session key for storing step data"""
    return f"company_reg_step{step}_{user_id}"


# ========== REGISTRATION STEPS ==========
@company_bp.route("/register/step1", methods=["POST"])
def register_step1():
    """
    Representative verification - Step 1
    Accepts form data or JSON with files
    """
    form = CompanyRegistrationStep1Form()
    
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors}), 400
    
    try:
        # Check if email already exists
        existing_user = User.query.filter_by(email=form.official_email.data).first()
        if existing_user:
            return jsonify({"success": False, "message": "Email already registered"}), 409
        
        # Generate and send OTP to email
        email_otp = generate_otp()
        session[f"email_otp_{form.official_email.data}"] = {
            "otp": email_otp,
            "expires_at": (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        }
        
        # Send OTP email (implement in email_utils)
        # send_otp_email(form.official_email.data, email_otp)
        
        # Generate and send OTP to phone
        phone_otp = generate_otp()
        session[f"phone_otp_{form.phone.data}"] = {
            "otp": phone_otp,
            "expires_at": (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        }
        
        # Send OTP SMS (implement in sms_utils)
        # send_otp_sms(form.phone.data, phone_otp)
        
        # Store step 1 data in session temporarily
        step1_key = get_session_key("temp", 1)
        session[step1_key] = {
            "representative_name": form.representative_name.data,
            "designation": form.designation.data,
            "official_email": form.official_email.data,
            "phone": form.phone.data,
            "linkedin_profile": form.linkedin.data or None,
        }
        
        # Handle file uploads
        if form.government_id.data:
            filename = save_upload_file(
                form.government_id.data,
                category="company_docs",
                subfolder="government_ids"
            )
            session[step1_key]["government_id_path"] = filename
        
        if form.authorization_letter.data:
            filename = save_upload_file(
                form.authorization_letter.data,
                category="company_docs",
                subfolder="auth_letters"
            )
            session[step1_key]["authorization_letter_path"] = filename
        
        session.modified = True
        
        return jsonify({
            "success": True,
            "message": "OTP sent to email and phone",
            "next_step": 2
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error processing step 1: {str(e)}"
        }), 500


@company_bp.route("/register/verify-otp", methods=["POST"])
def verify_otp():
    """Verify email and/or phone OTP"""
    data = request.get_json() or request.form.to_dict()
    
    email = data.get("email")
    email_otp = data.get("email_otp")
    phone_otp = data.get("phone_otp")
    
    step1_key = get_session_key("temp", 1)
    
    if not session.get(step1_key):
        return jsonify({"success": False, "message": "Registration session expired"}), 400
    
    results = {"email_verified": False, "phone_verified": False}
    
    # Verify email OTP
    if email and email_otp:
        stored = session.get(f"email_otp_{email}", {})
        if stored.get("otp") == email_otp:
            expires_at = datetime.fromisoformat(stored.get("expires_at", ""))
            if datetime.utcnow() < expires_at:
                results["email_verified"] = True
                session[step1_key]["email_otp_verified"] = True
            else:
                return jsonify({"success": False, "message": "Email OTP expired"}), 400
        else:
            return jsonify({"success": False, "message": "Invalid email OTP"}), 400
    
    # Verify phone OTP
    if phone_otp:
        phone = session[step1_key].get("phone")
        stored = session.get(f"phone_otp_{phone}", {})
        if stored.get("otp") == phone_otp:
            expires_at = datetime.fromisoformat(stored.get("expires_at", ""))
            if datetime.utcnow() < expires_at:
                results["phone_verified"] = True
                session[step1_key]["phone_otp_verified"] = True
            else:
                return jsonify({"success": False, "message": "Phone OTP expired"}), 400
        else:
            return jsonify({"success": False, "message": "Invalid phone OTP"}), 400
    
    session.modified = True
    return jsonify({"success": True, "results": results}), 200


@company_bp.route("/register/step2", methods=["POST"])
def register_step2():
    """Company details - Step 2"""
    form = CompanyRegistrationStep2Form()
    step1_key = get_session_key("temp", 1)
    
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors}), 400
    
    if not session.get(step1_key):
        return jsonify({"success": False, "message": "Complete step 1 first"}), 400
    
    # Verify OTPs were confirmed
    if not session[step1_key].get("email_otp_verified") or not session[step1_key].get("phone_otp_verified"):
        return jsonify({"success": False, "message": "Please verify email and phone OTPs"}), 400
    
    try:
        # Store step 2 data
        step2_key = get_session_key("temp", 2)
        session[step2_key] = {
            "company_legal_name": form.company_name.data,
            "corporate_id": form.corporate_id.data,
            "business_type": form.business_type.data,
            "incorporation_date": form.incorporation_date.data.isoformat() if form.incorporation_date.data else None,
            "company_email": form.company_email.data,
            "company_phone": form.company_phone.data,
            "website": form.website.data,
            "registered_address": form.registered_address.data,
        }
        session.modified = True
        
        return jsonify({
            "success": True,
            "message": "Company details saved",
            "next_step": 3
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error processing step 2: {str(e)}"
        }), 500


@company_bp.route("/register/step3", methods=["POST"])
def register_step3():
    """Document upload - Step 3"""
    form = CompanyRegistrationStep3Form()
    step2_key = get_session_key("temp", 2)
    
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors}), 400
    
    if not session.get(step2_key):
        return jsonify({"success": False, "message": "Complete step 2 first"}), 400
    
    try:
        step3_key = get_session_key("temp", 3)
        session[step3_key] = {}
        
        # Handle document uploads
        if form.incorporation_document.data:
            filename = save_upload_file(
                form.incorporation_document.data,
                category="company_docs",
                subfolder="incorporation"
            )
            session[step3_key]["incorporation_document_path"] = filename
        
        if form.tax_document.data:
            filename = save_upload_file(
                form.tax_document.data,
                category="company_docs",
                subfolder="tax_docs"
            )
            session[step3_key]["tax_document_path"] = filename
        
        if form.license_document.data:
            filename = save_upload_file(
                form.license_document.data,
                category="company_docs",
                subfolder="licenses"
            )
            session[step3_key]["license_document_path"] = filename
        
        session.modified = True
        
        return jsonify({
            "success": True,
            "message": "Documents uploaded",
            "next_step": 4
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error processing step 3: {str(e)}"
        }), 500


@company_bp.route("/register/step4", methods=["POST"])
def register_step4():
    """Security & consent, then create account - Step 4"""
    form = CompanyRegistrationStep4Form()
    
    step1_key = get_session_key("temp", 1)
    step2_key = get_session_key("temp", 2)
    step3_key = get_session_key("temp", 3)
    
    if not form.validate_on_submit():
        return jsonify({"success": False, "errors": form.errors}), 400
    
    if not session.get(step1_key) or not session.get(step2_key):
        return jsonify({"success": False, "message": "Complete previous steps first"}), 400
    
    try:
        # Gather all data from session
        step1_data = session[step1_key]
        step2_data = session[step2_key]
        step3_data = session.get(step3_key, {})
        
        # Hash password (import from auth routes)
        from app.blueprints.auth.routes import hash_password
        
        # Create User account
        user = User(
            name=step2_data["company_legal_name"],
            email=step1_data["official_email"],
            password_hash=hash_password(form.password.data),
            role=RoleEnum.company,
            is_verified=False
        )
        db.session.add(user)
        db.session.flush()  # Get user ID before creating profile
        
        # Create CompanyProfile
        app_id = generate_application_id()
        company_profile = CompanyProfile(
            user_id=user.id,
            application_id=app_id,
            registration_step=5,
            status="verification_in_progress",
            # Step 1 data
            representative_name=step1_data.get("representative_name"),
            designation=step1_data.get("designation"),
            official_email=step1_data.get("official_email"),
            email_otp_verified=step1_data.get("email_otp_verified", False),
            phone=step1_data.get("phone"),
            phone_otp_verified=step1_data.get("phone_otp_verified", False),
            linkedin_profile=step1_data.get("linkedin_profile"),
            government_id_path=step1_data.get("government_id_path"),
            authorization_letter_path=step1_data.get("authorization_letter_path"),
            # Step 2 data
            company_legal_name=step2_data.get("company_legal_name"),
            corporate_id=step2_data.get("corporate_id"),
            business_type=step2_data.get("business_type"),
            incorporation_date=step2_data.get("incorporation_date"),
            company_email=step2_data.get("company_email"),
            company_phone=step2_data.get("company_phone"),
            website=step2_data.get("website"),
            registered_address=step2_data.get("registered_address"),
            # Step 3 data
            incorporation_document_path=step3_data.get("incorporation_document_path"),
            tax_document_path=step3_data.get("tax_document_path"),
            license_document_path=step3_data.get("license_document_path"),
            # Step 4 data
            terms_accepted=form.terms_consent.data,
            privacy_accepted=form.terms_consent.data,
            submitted_at=datetime.utcnow()
        )
        db.session.add(company_profile)
        db.session.commit()
        
        # Clear session data
        session.pop(step1_key, None)
        session.pop(step2_key, None)
        session.pop(step3_key, None)
        # Issue JWT and set HttpOnly cookie
        from app.blueprints.auth.routes import issue_token
        from flask_jwt_extended import set_access_cookies
        access_token = issue_token(user)

        response = jsonify({
            "success": True,
            "message": "Registration submitted successfully",
            "application_id": app_id,
            "status": "verification_in_progress",
            "next_step": 5,
            "redirect": "/company/dashboard"
        })
        set_access_cookies(response, access_token)
        return response, 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error creating account: {str(e)}"
        }), 500


# ========== COMPANY DASHBOARD ==========
@company_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    """Company dashboard"""
    raw_id = get_jwt_identity()
    user_id = int(raw_id) if raw_id else None
    user = User.query.get(user_id) if user_id else None
    
    role_str = user.role.value if user and hasattr(user.role, "value") else str(user.role if user else "")
    if not user or role_str != "company":
        return jsonify({"message": "Access denied"}), 403
    
    company = CompanyProfile.query.filter_by(user_id=user_id).first()
    if not company:
        return jsonify({"message": "Company profile not found"}), 404
    
    return render_template("company/dashboard.html", company=company, user=user)


@company_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """Get company profile"""
    user_id = get_jwt_identity()
    company = CompanyProfile.query.filter_by(user_id=user_id).first()
    
    if not company:
        return jsonify({"message": "Company profile not found"}), 404
    
    return jsonify({
        "application_id": company.application_id,
        "company_name": company.company_legal_name,
        "status": company.status,
        "website": company.website,
        "registered_address": company.registered_address,
        "verification_step": company.registration_step,
        "submitted_at": company.submitted_at.isoformat() if company.submitted_at else None,
        "verified_at": company.verified_at.isoformat() if company.verified_at else None,
    }), 200
