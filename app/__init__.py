from flask import Flask
from app.extensions import db, jwt, oauth, migrate
from app.blueprints.auth.routes import auth_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    jwt.init_app(app)
    oauth.init_app(app)
    migrate.init_app(app, db)

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