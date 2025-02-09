from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Product  # Assuming you have a Product model

product_bp = Blueprint("product", __name__)

# 🟢 Get all products
@product_bp.route("/", methods=["GET"])
def get_products():
    products = Product.query.all()
    return jsonify([product.to_dict() for product in products])

# 🟢 Get a single product by ID
@product_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())

# 🟢 Create a new product
@product_bp.route("/", methods=["POST"])
def create_product():
    data = request.json
    new_product = Product(
        name=data.get("name"),
        price=data.get("price"),
        description=data.get("description"),
        stock=data.get("stock", 0),
        category=data.get("category")
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Product created!", "product": new_product.to_dict()}), 201

# 🟢 Update an existing product
@product_bp.route("/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.json

    product.name = data.get("name", product.name)
    product.price = data.get("price", product.price)
    product.description = data.get("description", product.description)
    product.stock = data.get("stock", product.stock)
    product.category = data.get("category", product.category)

    db.session.commit()
    return jsonify({"message": "Product updated!", "product": product.to_dict()})

# 🟢 Delete a product
@product_bp.route("/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted!"})

