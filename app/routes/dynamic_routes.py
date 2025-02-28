from flask import Blueprint, request, render_template, jsonify

from app.models import User
from app.modules.CartManager.manager import CartManager
from app.modules.UserManager.manager import CustomerManager
from app.modules.SessionManager.manager import SessionManager
from app.modules.Middlewares.auth_middleware import login_required
from app.extensions import seraphina

dynamic_route_bp = Blueprint("dynamic_route", __name__)


@dynamic_route_bp.route("/order", methods=["GET"])
@login_required
def check_order():
    order_id = request.args.get("order_id")
    return render_template("order-confirmation.html", order_id=order_id)


@dynamic_route_bp.route("/checkout", methods=["GET"])
@login_required
def checkout_page():
    """Render the checkout page with order details."""
    try:
        session_id = request.cookies.get("session_id")
        user_id = SessionManager.get_user_id_by_session_id(session_id)

        if not user_id:
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        # Get user and cart details
        user = CustomerManager.get_user_by_id(user_id)
        cart_data = CartManager.get_cart(user_id)

        if not cart_data["success"] or not cart_data["items"]:
            return render_template("checkout.html", error="Your cart is empty.")

        # Calculate total price (subtotal + delivery charges)
        subtotal = sum(item["product_price"] * item["quantity"] for item in cart_data["items"])
        delivery_charges = int(0)  # Placeholder can be updated dynamically
        print(type(delivery_charges))
        total_price = subtotal + delivery_charges

        user_name = user.first_name + " " + user.last_name
        user_email = user.email

        # Render checkout page with user and cart data
        return render_template(
            "checkout.html",
            cart=cart_data["items"],
            total_price=total_price,
            delivery_charges=delivery_charges,
            user_phone=user.phone if user.phone else "Not provided",
            user_address=user.default_location if user.default_location else "",
            user_email=user_email,
            user_name=user_name
        )

    except Exception as e:
        seraphina.error(f"Error in checkout_page: {str(e)}")
        return render_template("checkout.html", error="An error occurred while loading checkout."), 500


