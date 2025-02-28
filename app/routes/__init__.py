from flask import Blueprint
from app.routes.product_routes import product_bp
from app.routes.static_routes import staticroute_bp
from app.routes.auth_routes import auth_bp
from app.routes.promotion_routes import promotion_bp
from app.routes.cart_routes import cart_bp
from app.routes.order_routes import order_bp
from app.routes.dynamic_routes import dynamic_route_bp
from app.routes.payment_routes import payment_bp


def register_blueprints(app):
    # API Routes
    app.register_blueprint(product_bp, url_prefix="/api/product")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(promotion_bp, url_prefix="/api/promotions")
    app.register_blueprint(cart_bp, url_prefix="/api/cart")
    app.register_blueprint(order_bp, url_prefix="/api/order")
    app.register_blueprint(payment_bp,url_prefix="/api/payment")

    # Static Routes
    app.register_blueprint(staticroute_bp, url_prefix="/")

    # Dynamic Routes
    app.register_blueprint(dynamic_route_bp, url_prefix="/")
