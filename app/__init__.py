from flask import Flask
from flask_migrate import Migrate

from app.Seraphina import Seraphina
from app.config import config
from app.extensions import db, seraphina, init_seraphina, init_redis, init_cache
from app.utils.template_utils import format_price
import os
from sqlalchemy import inspect


def create_app():
    app = Flask(__name__)

    # Load config
    env = os.getenv("ENV", "prod")
    app.config.from_object(config[env])

    # setting up helper utils

    app.jinja_env.filters['format_price'] = format_price

    # Initialize database
    db.init_app(app)

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)  # ADD THIS

    # Initialize Seraphina
    init_seraphina(app)

    # inits redis
    init_redis(app)  # Initialize Redis

    # init cache
    init_cache(app)

    # Register blueprints inside app context
    with app.app_context():
        global seraphina
        db.engine.connect()
        from app.routes import register_blueprints
        register_blueprints(app)

        app.context_processor(lambda: {
            "SHOP_NAME": app.config["SHOP_NAME"],
            "SHOP_EMAIL": app.config["SHOP_EMAIL"],
            "SHOP_PHONE": app.config["SHOP_PHONE"],
            "SHOP_ADDRESS": app.config["SHOP_ADDRESS"],
            "CURRENCY": app.config["CURRENCY"],
            "CURRENCY_SYMBOL": app.config["CURRENCY_SYMBOL"],
            "TAX_RATE": app.config["TAX_RATE"],
            "SHIPPING_COST": app.config["SHIPPING_COST"],
            "FREE_SHIPPING_THRESHOLD": app.config["FREE_SHIPPING_THRESHOLD"],
            "LOGO": app.config["LOGO"],
            "FAVICON": app.config["FAVICON"],
            "PRIMARY_COLOR": app.config["PRIMARY_COLOR"],
            "SECONDARY_COLOR": app.config["SECONDARY_COLOR"],
            "BACKGROUND_COLOR": app.config["BACKGROUND_COLOR"],
            "DARK_COLOR": app.config["DARK_COLOR"],
        })

        # Only create tables if necessary
        if "sqlite" in app.config["SQLALCHEMY_DATABASE_URI"]:
            db.create_all()

        inspector = inspect(db.engine)
        existing_tables = set(inspector.get_table_names())  # Get existing tables
        defined_tables = set(db.metadata.tables.keys())  # Get tables from models

        missing_tables = defined_tables - existing_tables  # Find tables that are missing

        if missing_tables:
            print(f"Creating missing tables: {', '.join(missing_tables)}")
            db.create_all()
        else:
            print("All tables exist. No new tables needed.")

    return app
