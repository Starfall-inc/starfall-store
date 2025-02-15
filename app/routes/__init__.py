from flask import Blueprint
from app.routes.product_routes import product_bp
from app.routes.static_routes import staticroute_bp
from app.routes.auth_routes import auth_bp


def register_blueprints(app):

    # API Routes
    app.register_blueprint(product_bp, url_prefix="/api/product")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # Static Routes
    app.register_blueprint(staticroute_bp, url_prefix="/")

