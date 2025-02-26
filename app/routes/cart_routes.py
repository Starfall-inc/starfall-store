from flask import Blueprint, request, jsonify
from app.modules.CartManager.manager import CartManager
from app.modules.SessionManager.manager import SessionManager
from app.modules.Middlewares.auth_middleware import login_required
from app.extensions import seraphina

cart_bp = Blueprint("cart", __name__)


def get_user_id():
    """Helper function to retrieve user_id from session."""
    session_id = request.cookies.get("session_id")
    user_id = SessionManager.get_user_id_by_session_id(session_id)
    if not user_id:
        seraphina.warn(f"Unauthorized access attempt with session_id: {session_id}")
    return user_id


@cart_bp.route("/", methods=["PUT"])
@login_required
def add_to_cart():
    """Add a product to the cart (or update quantity)."""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        data = request.get_json()
        product_id = data.get("product_id")
        quantity = data.get("quantity", 1)

        if not product_id:
            return jsonify({"success": False, "error": "Missing product_id"}), 400

        response = CartManager.add_to_cart(user_id, product_id, quantity)
        if response["success"]:
            seraphina.info(f"User {user_id} added product {product_id} to cart.")
        return jsonify(response), (200 if response["success"] else 400)

    except Exception as e:
        seraphina.error(f"Error in add_to_cart: {str(e)}")
        return jsonify({"success": False, "error": "Internal Server Error"}), 500


@cart_bp.route("/", methods=["GET"])
@login_required
def get_cart():
    """Retrieve the user's cart."""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        cart_data = CartManager.get_cart(user_id)
        return jsonify(cart_data), 200

    except Exception as e:
        seraphina.error(f"Error in get_cart: {str(e)}")
        return jsonify({"success": False, "error": "Internal Server Error"}), 500


@cart_bp.route("/", methods=["DELETE"])
@login_required
def clear_cart():
    """Clear all items from the user's cart."""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        response = CartManager.clear_cart(user_id)
        if response["success"]:
            seraphina.info(f"User {user_id} cleared their cart.")
        return jsonify(response), (200 if response["success"] else 400)

    except Exception as e:
        seraphina.error(f"Error in clear_cart: {str(e)}")
        return jsonify({"success": False, "error": "Internal Server Error"}), 500


@cart_bp.route("/<int:product_id>", methods=["DELETE"])
@login_required
def remove_from_cart(product_id):
    """Remove a specific product from the cart."""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        response = CartManager.remove_from_cart(user_id, product_id)
        if response["success"]:
            seraphina.info(f"User {user_id} removed product {product_id} from cart.")
        return jsonify(response), (200 if response["success"] else 400)

    except Exception as e:
        seraphina.error(f"Error in remove_from_cart: {str(e)}")
        return jsonify({"success": False, "error": "Internal Server Error"}), 500


@cart_bp.route("/", methods=["PATCH"])
@login_required
def update_cart():
    """Update cart item details (quantity, cart_id, etc.)."""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        data = request.get_json()
        product_id = data.get("product_id")

        if not product_id:
            return jsonify({"success": False, "error": "Missing product_id"}), 400

        # Filter out valid updatable fields
        updatable_fields = {key: data[key] for key in ["quantity", "cart_id"] if key in data}

        if not updatable_fields:
            return jsonify({"success": False, "error": "No valid fields to update"}), 400

        response = CartManager.update_cart(user_id, product_id, **updatable_fields)

        if response["success"]:
            seraphina.info(f"User {user_id} updated product {product_id} in cart: {updatable_fields}")
        return jsonify(response), (200 if response["success"] else 400)

    except Exception as e:
        seraphina.error(f"Error in update_cart: {str(e)}")
        return jsonify({"success": False, "error": "Internal Server Error"}), 500
