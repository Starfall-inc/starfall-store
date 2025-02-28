from flask import Blueprint, request, jsonify
from app.modules.PaymentManager.manager import PaymentManager
from app.modules.OrderManager.manager import OrderManager
from app.modules.SessionManager.manager import SessionManager
from app.modules.Middlewares.auth_middleware import login_required
from app.extensions import seraphina

payment_bp = Blueprint("payment", __name__)


def get_user_id():
    """Retrieve user_id from session securely."""
    session_id = request.cookies.get("session_id")
    return SessionManager.get_user_id_by_session_id(session_id)


@payment_bp.route("/initiate", methods=["POST"])
@login_required
def initiate_payment():
    """Initiate payment using Juspay with a verified order total from the server."""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        data = request.get_json()
        order_id = data.get("order_id")

        if not order_id:
            return jsonify({"success": False, "error": "Missing order_id"}), 400

        # ✅ Ensure the order belongs to the authenticated user
        order_data = OrderManager.get_orders(order_id=order_id)
        if not order_data["success"]:
            return jsonify({"success": False, "error": "Order not found or unauthorized"}), 403

        # ✅ Get the total price (including delivery charges) from the server
        total_price = order_data["order"]["total"]

        # ✅ Ensure the user cannot provide their own price
        response = PaymentManager.initiate_payment(order_id, total_price)

        if response["success"]:
            seraphina.info(f"🔵 Payment initiated for Order {order_id} by User {user_id}")
        return jsonify(response), (200 if response["success"] else 400)

    except Exception as e:
        seraphina.error(f"🔴 Error in initiate_payment: {str(e)}")
        return jsonify({"success": False, "error": "Internal Server Error"}), 500


@payment_bp.route("/callback", methods=["POST"])
def payment_callback():
    """Handle Juspay payment callback and update order status securely."""
    try:
        request_data = request.get_json()
        received_signature = request.headers.get("x-juspay-signature")

        # ✅ Verify Juspay Signature to prevent forged requests
        if not PaymentManager.verify_juspay_signature(request_data, received_signature):
            seraphina.warn(f"⚠️ Invalid Juspay signature! Possible attack detected.")
            return jsonify({"success": False, "error": "Unauthorized request"}), 403

        response = PaymentManager.process_payment_callback(request_data)

        if response["success"]:
            seraphina.info(f"✅ Payment successful for Order {request_data.get('order_id')}")
        else:
            seraphina.warn(f"❌ Payment failed for Order {request_data.get('order_id')}")

        return jsonify(response), (200 if response["success"] else 400)

    except Exception as e:
        seraphina.error(f"🔴 Error in payment_callback: {str(e)}")
        return jsonify({"success": False, "error": "Internal Server Error"}), 500
