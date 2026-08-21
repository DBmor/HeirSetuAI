# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()
jwt = JWTManager()
oauth = OAuth()


# ---------------------------------------------------------
# app/__init__.py  (create_app factory — relevant part only)
# ---------------------------------------------------------
"""
from flask import Flask
from app.extensions import db, jwt, oauth
from app.blueprints.auth.routes import auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    jwt.init_app(app)
    oauth.init_app(app)

    oauth.register(
        name="google",
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

    app.register_blueprint(auth_bp)

    @app.route("/login")
    @app.route("/register")
    def auth_page():
        from flask import render_template
        return render_template("auth/auth.html")

    return app
"""

# ---------------------------------------------------------
# config.py  (relevant keys only)
# ---------------------------------------------------------
"""
import os

class Config:
    SECRET_KEY = os.environ["SECRET_KEY"]
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URI"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 24  # 24 hours, tune as needed

    GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
    GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
"""

# ---------------------------------------------------------
# .env  (add these — never commit this file)
# ---------------------------------------------------------
"""
SECRET_KEY=change-me
DATABASE_URI=sqlite:///job_platform.db
JWT_SECRET_KEY=change-me-too
GOOGLE_CLIENT_ID=xxxxxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxxxxxxx
"""
