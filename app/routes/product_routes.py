from flask import Blueprint, request, jsonify
from app.extensions import db,logger
from app.modules.ProductManager import ProductManager


product_bp = Blueprint("product", __name__)

# Ensure logger is initialized inside an app context
if logger is None:
    print("[ERROR] Logger is not initialized. Call init_logger() inside an app context.")


# 🟢 Get all products
@product_bp.route("/", methods=["GET"])
def get_products():
    products = ProductManager.get_all_products()
    logger.success("Fetched All Products")
    return jsonify([product.to_dict() for product in products])

# 🟢 Get a single product by ID
@product_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):
    # product = Product.query.get_or_404(product_id)
    product = ProductManager.get_product_by_id(product_id)
    return jsonify(product.to_dict())


