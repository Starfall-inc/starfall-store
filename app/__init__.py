from flask import Flask
from flask_migrate import Migrate
from app.Seraphina import Seraphina
from app.config import config
from app.extensions import admin_db, db, seraphina, init_seraphina, init_redis, init_cache, oauth, init_oauth
from app.utils.template_utils import format_price
import os
from sqlalchemy import inspect
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# ✅ Global variable to store enabled OAuth providers
ENABLED_OAUTH_PROVIDERS = {}


def create_app():
    app = Flask(__name__)

    # Load config
    env = os.getenv("ENV", "prod")
    app.config.from_object(config[env])

    # Setting up helper utils
    app.jinja_env.filters['format_price'] = format_price

    # Initialize database
    db.init_app(app)

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    # Initialize Seraphina
    init_seraphina(app)

    # Initialize Redis
    init_redis(app)

    # Initialize Cache
    init_cache(app)

    # ✅ Initialize OAuth Providers (Google, Facebook, etc.)
    init_oauth(app)

    # ✅ Store enabled OAuth providers dynamically
    global ENABLED_OAUTH_PROVIDERS

    print(app.config.get("GOOGLE_CLIENT_ID"))
    print(app.config.get("FACEBOOK_CLIENT_ID"))

    ENABLED_OAUTH_PROVIDERS = {
        "google": bool(app.config.get("GOOGLE_CLIENT_ID")),
        "facebook": bool(app.config.get("FACEBOOK_CLIENT_ID"))
    }

    print(f"Enabled OAuth providers: {ENABLED_OAUTH_PROVIDERS}")

    # Register blueprints inside app context
    with app.app_context():
        global seraphina
        db.engine.connect()

        # Import models early to ensure they are registered
        from app.models import admin_models  # Import all models before creating tables

        from app.routes import register_blueprints
        register_blueprints(app)

        # Inject global settings into templates
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
            "ENABLED_OAUTH_PROVIDERS": ENABLED_OAUTH_PROVIDERS  # ✅ Inject enabled OAuth providers
        })



        # ✅ Auto-create tables if necessary
        if "sqlite" in app.config["SQLALCHEMY_DATABASE_URI"]:
            db.create_all()

        inspector = inspect(db.engine)
        existing_tables = set(inspector.get_table_names())  # Get existing tables
        defined_tables = set(db.metadata.tables.keys())  # Get tables from models

        missing_tables = defined_tables - existing_tables  # Find missing tables

        if missing_tables:
            print(f"Creating missing tables: {', '.join(missing_tables)}")
            db.create_all()
        else:
            print("All tables exist. No new tables needed.")

        # Create tables for bound databases
        for bind_name in app.config["SQLALCHEMY_BINDS"]:
            try:
                # Import admin models to ensure they're registered
                if bind_name == "admin_db":
                    from app.models import admin_models  # Import models for the admin_db bind

                db.create_all(bind_key=bind_name)
                print(f"Tables created for bind: {bind_name}")
            except Exception as e:
                print(f"Error creating tables for bind {bind_name}: {e}")
                import traceback
                traceback.print_exc()

    return app
