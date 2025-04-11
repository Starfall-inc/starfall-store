from flask import Flask
from flask_migrate import Migrate
from app.Seraphina import Seraphina
from app.config import config
from app.extensions import admin_db, db, seraphina, init_seraphina, init_redis, init_cache, oauth, init_oauth, \
    init_minio
from app.utils.template_utils import format_price
import os
from sqlalchemy import inspect
from pathlib import Path
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# ✅ Global variable to store enabled OAuth providers
ENABLED_OAUTH_PROVIDERS = {}

CONFIG_PATH = Path(__file__).parent.parent / "app/config.json"


def load_config():
    """Loads the latest config from config.json dynamically."""
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Error loading config: {e}")
        return {}  # Return an empty dictionary on failure


def create_app():
    app = Flask(__name__)

    # Load config
    env = os.getenv("ENV", "prod")
    app.config.from_object(config[env])

    # Setting up helper utils
    app.jinja_env.filters['format_price'] = format_price

    app.config["DEBUG"] = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True  # Reloads templates without restart

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

    # Init Minio
    init_minio(app)

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

        @app.context_processor
        def inject_settings():
            """Loads config.json dynamically each time a template is rendered."""
            config_data = load_config()

            if not config_data:
                return {}  # Avoid errors if config loading fails

            shop = config_data.get("shop", {})

            return {
                "SHOP_NAME": shop.get("name", "Default Shop"),
                "SHOP_EMAIL": shop.get("email", "support@example.com"),
                "SHOP_PHONE": shop.get("phone", "000-000-0000"),
                "SHOP_ADDRESS": shop.get("address", "123 Default St."),
                "CURRENCY": shop.get("currency", "USD"),
                "CURRENCY_SYMBOL": shop.get("currency_symbol", "$"),
                "TAX_RATE": shop.get("tax", 0.0),
                "SHIPPING_COST": shop.get("shipping", 0),
                "FREE_SHIPPING_THRESHOLD": shop.get("free_shipping", 0),
                "LOGO": shop.get("logo", "default-logo.png"),
                "FAVICON": shop.get("favicon", "default-favicon.ico"),
                "PRIMARY_COLOR": shop.get("theme", {}).get("primary", "#000000"),
                "SECONDARY_COLOR": shop.get("theme", {}).get("secondary", "#FFFFFF"),
                "TEXT_COLOR": shop.get("theme", {}).get("text", "#333333"),
                "BACKGROUND_COLOR": shop.get("theme", {}).get("background", "#F8F8F8"),
                "DARK_COLOR": shop.get("theme", {}).get("dark", "#111111"),
                "ENABLED_OAUTH_PROVIDERS": ENABLED_OAUTH_PROVIDERS,  # Add this line
            }

        return app

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
