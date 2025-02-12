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

    return app
