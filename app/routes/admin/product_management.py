from flask import Blueprint, request, jsonify
from app.modules.Admin.ProductManager import ProductManager

product_bp = Blueprint("admin_product", __name__)


@product_bp.route("/category", methods=["POST"])
def create_category():
    """Route to create a new product category."""
    data = request.json
    name = data.get("name")
    description = data.get("description")
    category_image = data.get("category_image")  # URL or file path

    response, status_code = ProductManager.create_category(name, description, category_image)
    return jsonify(response), status_code


@product_bp.route("/", methods=["POST"])
def create_product():
    """Route to create a new product."""
    name = request.form.get("name")
    description = request.form.get("description")
    category_id = request.form.get("category_id")
    price = float(request.form.get("price"))
    stock_quantity = int(request.form.get("stock_quantity"))
    weight = float(request.form.get("weight"))
    tags = request.form.getlist("tags")  # Expecting multiple values
    attributes = request.form.get("attributes", {})  # JSON field
    is_featured = bool(request.form.get("is_featured", False))

    # Handle image uploads
    images = request.files.getlist("images")

    response, status_code = ProductManager.create_product(
        name, description, category_id, price, stock_quantity, weight, tags, attributes, images, is_featured
    )
    return jsonify(response), status_code
