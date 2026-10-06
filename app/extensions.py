from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from authlib.integrations.flask_client import OAuth
from flask_migrate import Migrate
from flask_mail import Mail

db = SQLAlchemy()
jwt = JWTManager()
oauth = OAuth()
migrate = Migrate()
mail = Mail()