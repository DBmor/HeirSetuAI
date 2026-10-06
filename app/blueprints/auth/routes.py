# app/blueprints/auth/routes.py
from flask import Blueprint, request, jsonify, redirect, url_for, session, render_template
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity, set_access_cookies, unset_jwt_cookies
import bcrypt

from app.extensions import db, oauth
from app.models.user import User, CompanyProfile, RoleEnum

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# ---------- helpers ----------
def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def check_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def issue_token(user: User) -> str:
    # role goes into the JWT as a claim — every protected route reads this,
    # instead of hitting the DB again to check who's allowed where.
    role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
    return create_access_token(
        identity=str(user.id),
        additional_claims={"role": role_str},
    )


# ---------- page routes ----------
@auth_bp.route("/login", methods=["GET"])
def login_page():
    """Render login page"""
    return render_template("auth/login.html")


@auth_bp.route("/register-candidate", methods=["GET"])
def register_candidate_page():
    """Render candidate registration page"""
    return render_template("auth/register_candidate.html")


@auth_bp.route("/register-company", methods=["GET"])
def register_company_page():
    """Render company registration page"""
    return render_template("auth/register_company.html")


# ---------- register ----------
@auth_bp.route("/register", methods=["POST"])
def register():
    # Handle both JSON and form data
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    role = data.get("role")
    email = data.get("email", "").strip().lower()
    password = data.get("password")
    name = data.get("name")
    company_name = data.get("company_name")
    website = data.get("website")

    if role not in ("candidate", "company"):
        return jsonify({"message": "Invalid role."}), 400
    
    # For candidates, require 'name'; for companies, require 'company_name' and 'website'
    if role == "candidate" and (not email or not password or not name):
        return jsonify({"message": "Name, email, and password are required."}), 400
    if role == "company" and (not email or not password or not company_name or not website):
        return jsonify({"message": "Company name, website, email, and password are required."}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "An account with this email already exists."}), 409

    user = User(
        name=company_name if role == "company" else name,
        email=email,
        password_hash=hash_password(password),
        role=RoleEnum(role),
    )
    db.session.add(user)
    db.session.flush()  # get user.id before commit

    if role == "company":
        profile = CompanyProfile(
            user_id=user.id,
            website=website,
            industry=data.get("industry"),
            employee_count=data.get("employee_count"),
            status="pending",
        )
        db.session.add(profile)

    db.session.commit()

    token = issue_token(user)
    redirect_url = "/candidate/home" if role == "candidate" else "/company/dashboard"
    
    if request.is_json:
        response = jsonify({"access_token": token, "role": role, "redirect": redirect_url})
        set_access_cookies(response, token)
        return response, 201
    else:
        response = redirect(redirect_url)
        set_access_cookies(response, token)
        return response


# ---------- login ----------
@auth_bp.route("/login", methods=["POST"])
def login_post():
    # Handle both JSON and form data
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    email = data.get("email", "").strip().lower()
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not user.password_hash or not check_password(password, user.password_hash):
        error_msg = {"message": "Invalid email or password."}
        if request.is_json:
            return jsonify(error_msg), 401
        else:
            return render_template("auth/login.html", error=error_msg["message"]), 401

    token = issue_token(user)
    user_role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
    redirect_url = "/candidate/home" if user_role_str == "candidate" else "/company/dashboard"
    
    if request.is_json:
        response = jsonify({"access_token": token, "role": user_role_str, "redirect": redirect_url})
        set_access_cookies(response, token)
        return response, 200
    else:
        response = redirect(redirect_url)
        set_access_cookies(response, token)
        return response


# ---------- logout ----------
@auth_bp.route("/logout", methods=["GET", "POST"])
def logout():
    """Logout route clearing JWT HttpOnly cookies"""
    response = redirect(url_for("auth.login_page"))
    unset_jwt_cookies(response)
    return response


# ---------- Google OAuth ----------
@auth_bp.route("/google")
@auth_bp.route("/google/login")
def google_login():
    # role is passed from the frontend button so the callback knows
    # whether to create a candidate or a company account
    role = request.args.get("role", "candidate")
    if role not in ("candidate", "company"):
        role = "candidate"
    session["oauth_role"] = role
    redirect_uri = url_for("auth.google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route("/google/callback")
def google_callback():
    token = oauth.google.authorize_access_token()
    userinfo = token.get("userinfo")  # {'email': ..., 'name': ..., 'sub': google_id, ...}

    role = session.pop("oauth_role", "candidate")
    email = userinfo["email"].lower()

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            name=userinfo.get("name", email.split("@")[0]),
            email=email,
            google_id=userinfo["sub"],
            role=RoleEnum(role),
            is_verified=True,
        )
        db.session.add(user)
        db.session.flush()
        if role == "company":
            db.session.add(CompanyProfile(
                user_id=user.id,
                industry=session.pop("company_industry", None),
                employee_count=session.pop("company_employee_count", None),
                status="pending"
            ))
        db.session.commit()
    elif not user.google_id:
        user.google_id = userinfo["sub"]
        db.session.commit()

    jwt_token = issue_token(user)
    user_role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
    frontend_redirect = "/candidate/home" if user_role_str == "candidate" else "/company/dashboard"
    response = redirect(frontend_redirect)
    set_access_cookies(response, jwt_token)
    return response


# ---------- role guard decorator, used across the app ----------
def role_required(required_role: str):
    from functools import wraps

    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if claims.get("role") != required_role:
                accept = request.headers.get("Accept", "")
                if "text/html" in accept or request.accept_mimetypes.accept_html:
                    return redirect(url_for("auth.login_page"))
                return jsonify({"message": "Forbidden — wrong account type."}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# ---------- example protected route ----------
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user = User.query.get(get_jwt_identity())
    return jsonify({"id": user.id, "name": user.name, "role": user.role.value})

