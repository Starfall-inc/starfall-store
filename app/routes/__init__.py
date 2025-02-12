from flask import Blueprint
from app.routes.product_routes import product_bp
from app.routes.static_routes import staticroute_bp

def register_blueprints(app):
    app.register_blueprint(product_bp, url_prefix="/product")
    app.register_blueprint(staticroute_bp, url_prefix="/")
