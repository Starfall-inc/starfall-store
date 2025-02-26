from flask import Blueprint, request, jsonify
from app.modules.CartManager.manager import CartManager
from app.modules.SessionManager.manager import SessionManager
from app.modules.Middlewares.auth_middleware import login_required

cart_bp = Blueprint("cart", __name__)


@cart_bp.route("/", methods=["PUT"])
@login_required
def add_to_cart():
    """Add a product to the cart (or update quantity)."""
    try:
        session_id = request.cookies.get("session_id")
        user_id = SessionManager.get_user_id_by_session_id(session_id)

        if not user_id:
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        data = request.get_json()
        product_id = data.get("product_id")
        quantity = data.get("quantity", 1)

        if not product_id:
            return jsonify({"success": False, "error": "Missing product_id"}), 400

        response = CartManager.add_to_cart(user_id, product_id, quantity)
        return jsonify(response), (200 if response["success"] else 400)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@cart_bp.route("/", methods=["GET"])
@login_required
def get_cart():
    """Retrieve the user's cart."""
    try:
        session_id = request.cookies.get("session_id")
        user_id = SessionManager.get_user_id_by_session_id(session_id)

        if not user_id:
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        cart_data = CartManager.get_cart(user_id)
        return jsonify(cart_data), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@cart_bp.route("/", methods=["DELETE"])
@login_required
def clear_cart():
    """Clear all items from the user's cart."""
    try:
        session_id = request.cookies.get("session_id")
        user_id = SessionManager.get_user_id_by_session_id(session_id)

        if not user_id:
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        response = CartManager.clear_cart(user_id)
        return jsonify(response), (200 if response["success"] else 400)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@cart_bp.route("/<int:product_id>", methods=["DELETE"])
@login_required
def remove_from_cart(product_id):
    """Remove a specific product from the cart."""
    try:
        session_id = request.cookies.get("session_id")
        user_id = SessionManager.get_user_id_by_session_id(session_id)

        if not user_id:
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        response = CartManager.remove_from_cart(user_id, product_id)
        return jsonify(response), (200 if response["success"] else 400)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
