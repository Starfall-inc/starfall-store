from flask import Flask
from app.config import config
from app.extensions import db, init_logger  # Ensure you're using the same `db` instance
import os

def create_app():
    app = Flask(__name__)

    # Load config
    env = os.getenv("ENV", "prod")
    app.config.from_object(config[env])

    # Initialize database
    db.init_app(app)

    # Register blueprints inside app context
    with app.app_context():
        from app.routes import register_blueprints
        register_blueprints(app)
        init_logger()

        # Only create tables if necessary
        if "sqlite" in app.config["SQLALCHEMY_DATABASE_URI"]:
            db.create_all()

    return app
