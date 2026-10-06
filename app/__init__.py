from flask import Flask, redirect, url_for, render_template, jsonify, request
from app.extensions import db, jwt, oauth, migrate, mail
from app.blueprints.auth.routes import auth_bp
from app.blueprints.company.routes import company_bp
from app.blueprints.candidate.routes import candidate_bp
from app.blueprints.jobs.routes import jobs_bp
from app.blueprints.chat.routes import chat_bp
from app.blueprints.admin.routes import admin_bp
from app.blueprints.api.routes import api_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    jwt.init_app(app)
    oauth.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    with app.app_context():
        from app.models import User, CandidateProfile, CompanyProfile, Job, Resume, Application, Chat, Notification, Report, Admin
        db.create_all()

    # JWT Error Loaders: Redirect browser page requests to login, return JSON for API requests
    def is_html_request():
        if request.path.startswith("/api/") or request.is_json:
            return False
        accept = request.headers.get("Accept", "")
        return "text/html" in accept or request.accept_mimetypes.accept_html

    @jwt.unauthorized_loader
    def custom_unauthorized_response(err_str):
        app.logger.error(f"[JWT DEBUG] Unauthorized: '{err_str}' for path: {request.path}, Cookies received: {list(request.cookies.keys())}")
        if is_html_request():
            return redirect(url_for("auth.login_page"))
        return jsonify({"message": err_str}), 401

    @jwt.expired_token_loader
    def custom_expired_response(jwt_header, jwt_payload):
        app.logger.error(f"[JWT DEBUG] Expired token for path: {request.path}")
        if is_html_request():
            return redirect(url_for("auth.login_page"))
        return jsonify({"message": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def custom_invalid_token_response(err_str):
        app.logger.error(f"[JWT DEBUG] Invalid token: '{err_str}' for path: {request.path}")
        if is_html_request():
            return redirect(url_for("auth.login_page"))
        return jsonify({"message": "Invalid token"}), 401

    oauth.register(
        name="google",
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(candidate_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # Home / Landing page
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/login")
    def login_redirect():
        return redirect(url_for("auth.login_page"))

    @app.route("/register")
    def register_redirect():
        return redirect(url_for("auth.register_candidate_page"))

    return app
