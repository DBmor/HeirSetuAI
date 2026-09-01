# app/blueprints/auth/routes.py
from flask import Blueprint, request, jsonify, redirect, url_for, session
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity
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
    return create_access_token(
        identity=user.id,
        additional_claims={"role": user.role.value},
    )


# ---------- register ----------
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    role = data.get("role")
    email = data.get("email", "").strip().lower()
    password = data.get("password")
    name = data.get("name")

    if role not in ("candidate", "company"):
        return jsonify({"message": "Invalid role."}), 400
    if not email or not password or not name:
        return jsonify({"message": "Name, email, and password are required."}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "An account with this email already exists."}), 409

    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role=RoleEnum(role),
    )
    db.session.add(user)
    db.session.flush()  # get user.id before commit

    if role == "company":
        profile = CompanyProfile(
            user_id=user.id,
            website=data.get("website"),
            status="pending",
        )
        db.session.add(profile)
        # NOTE: trigger Agent 3 (fake_company_detector) here, async via Celery:
        # from app.tasks.company_check_tasks import run_company_check
        # run_company_check.delay(user.id)

    db.session.commit()

    token = issue_token(user)
    return jsonify({"access_token": token, "role": role}), 201


# ---------- login ----------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not user.password_hash or not check_password(password, user.password_hash):
        return jsonify({"message": "Invalid email or password."}), 401

    token = issue_token(user)
    return jsonify({"access_token": token, "role": user.role.value}), 200


# ---------- Google OAuth ----------
@auth_bp.route("/google/login")
def google_login():
    # role is passed from the frontend button so the callback knows
    # whether to create a candidate or a company account
    session["oauth_role"] = request.args.get("role", "candidate")
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
            db.session.add(CompanyProfile(user_id=user.id, status="pending"))
        db.session.commit()
    elif not user.google_id:
        user.google_id = userinfo["sub"]
        db.session.commit()

    jwt_token = issue_token(user)
    # redirect back to frontend with the token; frontend JS picks it up and stores it
    frontend_redirect = "/candidate/home" if user.role == RoleEnum.candidate else "/company/dashboard"
    return redirect(f"{frontend_redirect}?token={jwt_token}")


# ---------- role guard decorator, used across the app ----------
def role_required(required_role: str):
    from functools import wraps

    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if claims.get("role") != required_role:
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
