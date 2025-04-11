from flask import Blueprint

from app.routes.admin.static_pages_routes import admin_static_routes_bp
from app.routes.admin.order_management import order_blueprint
from app.routes.product_routes import product_bp
from app.routes.static_routes import staticroute_bp
from app.routes.auth_routes import auth_bp
from app.routes.promotion_routes import promotion_bp
from app.routes.cart_routes import cart_bp
from app.routes.order_routes import order_bp
from app.routes.dynamic_routes import dynamic_route_bp
from app.routes.payment_routes import payment_bp
from app.routes.admin.product_management import product_bp as admin_product_bp
from app.routes.invoice_routes import receipt_bp
from app.routes.admin.store_config_routes import admin_api


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

    # Admin Routes (static)
    app.register_blueprint(admin_static_routes_bp, url_prefix="/admin")

    # Admin Routes (API)
    app.register_blueprint(admin_product_bp)
    app.register_blueprint(order_blueprint, url_prefix="/api/admin/order")
    app.register_blueprint(receipt_bp)
    app.register_blueprint(admin_api, url_prefix="/admin/settings")

