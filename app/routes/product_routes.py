from flask import Blueprint, request, jsonify
from app.extensions import db
from app.extensions import seraphina as logger
from app.modules.ProductManager import ProductManager
from app.modules.ReviewManager import ReviewManager

product_bp = Blueprint("product", __name__)

# Ensure logger is initialized inside an app context
if logger is None:
    print("[ERROR] Logger is not initialized. Call init_logger() inside an app context.")


# 🟢 Get all products
@product_bp.route("/", methods=["GET"])
def get_products():
    products = ProductManager.get_all_products()
    return jsonify([product for product in products])


# 🟢 Get a single product by ID
@product_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):
    # product = Product.query.get_or_404(product_id)
    product = ProductManager.get_product_by_id(product_id)
    return jsonify(product.to_dict())


# 🟢 get a product's review
@product_bp.route("/<int:product_id>/reviews", methods=["GET"])
def get_reviews(product_id):
    reviews = ReviewManager.get_reviews(product_id)
    return jsonify([review.to_dict() for review in reviews])
