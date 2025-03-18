from flask import Blueprint, request, jsonify
from app.models.models import User, Order, OrderDetail, Product
from app.extensions import db
from datetime import datetime

admin_order_management_routes_bp = Blueprint("admin_order_management", __name__, url_prefix="/api/admin/order")


# ✅ Get all orders (Admin)
@admin_order_management_routes_bp.route("/", methods=["GET"])
def get_all_orders():
    orders = Order.query.all()
    return jsonify([{
        "id": order.id,
        "user_id": order.user_id,
        "payment_method": order.payment_method,
        "order_place_date": order.order_place_date,
        "expected_delivery_date": order.expected_delivery_date,
        "actual_delivery_date": order.actual_delivery_date,
        "is_completed": order.is_completed,
        "total": float(order.total),
        "shipping_address": order.shipping_address,
        "status": order.status,
        "delivery_charges": float(order.delivery_charges),
        "coordinate_lat": order.coordinate_lat,
        "coordinate_lon": order.coordinate_lon,
        "order_details": [{
            "product_id": detail.product_id,
            "quantity": detail.quantity,
            "price": float(detail.price),
            "subtotal": float(detail.subtotal)
        } for detail in order.order_details]
    } for order in orders]), 200


# ✅ Get a single order by ID (Admin)
@admin_order_management_routes_bp.route("/<int:order_id>", methods=["GET"])
def get_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    return jsonify({
        "id": order.id,
        "user_id": order.user_id,
        "payment_method": order.payment_method,
        "order_place_date": order.order_place_date,
        "expected_delivery_date": order.expected_delivery_date,
        "actual_delivery_date": order.actual_delivery_date,
        "is_completed": order.is_completed,
        "total": float(order.total),
        "shipping_address": order.shipping_address,
        "status": order.status,
        "delivery_charges": float(order.delivery_charges),
        "coordinate_lat": order.coordinate_lat,
        "coordinate_lon": order.coordinate_lon,
        "order_details": [{
            "product_id": detail.product_id,
            "quantity": detail.quantity,
            "price": float(detail.price),
            "subtotal": float(detail.subtotal)
        } for detail in order.order_details]
    }), 200


# ✅ Create a new order (Admin)
@admin_order_management_routes_bp.route("/", methods=["POST"])
def create_order():
    data = request.json

    # Validate User
    user = User.query.get(data.get("user_id"))
    if not user:
        return jsonify({"error": "Invalid user ID"}), 400

    # Validate Products & Calculate Order Total
    total_amount = 0
    order_details = []
    for item in data.get("products", []):
        product = Product.query.get(item["product_id"])
        if not product:
            return jsonify({"error": f"Product ID {item['product_id']} not found"}), 400
        if product.stock_quantity < item["quantity"]:
            return jsonify({"error": f"Insufficient stock for Product ID {item['product_id']}"}), 400

        subtotal = float(product.price) * item["quantity"]
        total_amount += subtotal
        order_details.append(OrderDetail(
            product_id=item["product_id"],
            quantity=item["quantity"],
            price=product.price,
            subtotal=subtotal
        ))

        # Reduce stock quantity
        product.stock_quantity -= item["quantity"]

    # Add delivery charges
    total_amount += float(data.get("delivery_charges", 0.00))

    # Create Order
    new_order = Order(
        user_id=data.get("user_id"),
        payment_method=data.get("payment_method"),
        order_place_date=datetime.utcnow(),
        expected_delivery_date=data.get("expected_delivery_date"),
        shipping_address=data.get("shipping_address"),
        status=data.get("status", "pending"),
        total=total_amount,
        delivery_charges=data.get("delivery_charges", 0.00),
        coordinate_lat=data.get("coordinate_lat"),
        coordinate_lon=data.get("coordinate_lon")
    )

    db.session.add(new_order)
    db.session.flush()  # Get the order ID before committing

    # Assign order details to the new order
    for detail in order_details:
        detail.order_id = new_order.id
        db.session.add(detail)

    db.session.commit()

    return jsonify({"message": "Order created successfully!", "order_id": new_order.id}), 201


# ✅ Update an order (Admin) using kwargs
@admin_order_management_routes_bp.route("/<int:order_id>", methods=["PUT"])
def update_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    data = request.json

    # Extract only the fields that exist in the Order model and are provided in the request
    valid_fields = {
        "payment_method", "expected_delivery_date", "actual_delivery_date", "is_completed",
        "total", "shipping_address", "status", "delivery_charges", "coordinate_lat", "coordinate_lon"
    }

    # Use kwargs to update only provided fields
    update_data = {key: value for key, value in data.items() if key in valid_fields}

    if update_data:
        for key, value in update_data.items():
            setattr(order, key, value)

        db.session.commit()
        return jsonify({"message": "Order updated successfully", "updated_fields": update_data}), 200
    else:
        return jsonify({"error": "No valid fields provided for update"}), 400



# ✅ Delete an order (Admin)
@admin_order_management_routes_bp.route("/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    # Restore stock quantities before deleting the order
    for detail in order.order_details:
        product = Product.query.get(detail.product_id)
        if product:
            product.stock_quantity += detail.quantity

    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": "Order deleted successfully"}), 200
