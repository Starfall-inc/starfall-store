from flask import Blueprint, request, jsonify

from app.models import Order
from app.modules.OrderManager.manager import OrderManager
from app.modules.PaymentManager.manager import PaymentManager
from app.modules.SessionManager.manager import SessionManager
from app.modules.Middlewares.auth_middleware import login_required
from app.extensions import seraphina

order_bp = Blueprint("order", __name__)


def get_user_id():
    """Retrieve user_id from session securely."""
    session_id = request.cookies.get("session_id")
    user_id = SessionManager.get_user_id_by_session_id(session_id)
    print(f" User id : {user_id} from {session_id}")
    return user_id


@order_bp.route("/", methods=["POST"])
@login_required
def place_order():
    """
    Create an order using cart contents and store user’s shipping address.

    🚀 **Frontend Workflow**:
    1️⃣ **User confirms order** → Calls this route.
    2️⃣ **Order is created** → Returns `order_id`.
    3️⃣ **Frontend redirects user to `/api/payment/initiate`** to pay.
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        data = request.get_json()
        shipping_address = data.get("shipping_address")
        delivery_charges = 0.00  # TODO: Implement dynamic delivery charges

        if not shipping_address:
            return jsonify({"success": False, "error": "Missing shipping_address"}), 400

        response = OrderManager.place_order(user_id, shipping_address, delivery_charges)

        if response["success"]:
            seraphina.info(f"✅ Order {response['order_id']} placed by User {user_id}")
            return jsonify(response), 201

        return jsonify(response), 400

    except Exception as e:
        seraphina.error(f"🔴 Error in place_order: {str(e)}")
        return jsonify({"success": False, "error": "Internal Server Error"}), 500


@order_bp.route("/<int:order_id>/pay", methods=["POST"])
@login_required
def initiate_payment_for_order(order_id):
    """
    🚀 **Step 2: Initiate Juspay Payment**
    - This route is called after an order is placed.
    - Redirects the user to Juspay’s payment page.
    """
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        # ✅ Ensure the order belongs to the authenticated user
        order_data = OrderManager.get_orders(order_id=order_id)
        print(order_data)
        if not order_data["success"] or order_data["orders"][0]["order_id"] != order_id:
            return jsonify({"success": False, "error": "Order not found or unauthorized"}), 403

        #access the user id from the order object.
        order = Order.query.get(order_id)
        if order.user_id != user_id:
            return jsonify({"success": False, "error": "Order not found or unauthorized"}), 403

        # ✅ Get the total price (including delivery charges) from the server
        total_price = order_data["orders"][0]["total"]

        # ✅ Initiate Juspay Payment
        response = PaymentManager.initiate_payment(order_id, total_price)

        if response["success"]:
            seraphina.info(f"💰 Payment initiated for Order {order_id} by User {user_id}")
        return jsonify(response), (200 if response["success"] else 400)

    except Exception as e:
        seraphina.error(f"🔴 Error in initiate_payment_for_order: {str(e)}")
        return jsonify({"success": False, "error": "Internal Server Error"}), 500


@order_bp.route("/", methods=["GET"])
@login_required
def get_orders():
    """Retrieve all orders for the authenticated user."""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        orders = OrderManager.get_orders(user_id=user_id)
        return jsonify(orders), 200

    except Exception as e:
        seraphina.error(f"Error in get_orders: {str(e)}")
        return jsonify({"success": False, "error": "Internal Server Error"}), 500


@order_bp.route("/<int:order_id>", methods=["GET"])
@login_required
def get_order_details(order_id):
    """Retrieve a specific order by order_id."""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        orders = OrderManager.get_orders(user_id=user_id)
        order = next((o for o in orders["orders"] if o["order_id"] == order_id), None)

        if not order:
            return jsonify({"success": False, "error": "Order not found"}), 404

        return jsonify({"success": True, "order": order}), 200

    except Exception as e:
        seraphina.error(f"Error in get_order_details: {str(e)}")
        return jsonify({"success": False, "error": "Internal Server Error"}), 500


@order_bp.route("/<int:order_id>", methods=["DELETE"])
@login_required
def cancel_order(order_id):
    """Cancel an order if it's not shipped or delivered."""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False, "error": "Unauthorized"}), 401

        response = OrderManager.cancel_order(order_id)

        if response["success"]:
            seraphina.info(f"User {user_id} canceled order {order_id}.")
        return jsonify(response), (200 if response["success"] else 400)

    except Exception as e:
        seraphina.error(f"Error in cancel_order: {str(e)}")
        return jsonify({"success": False, "error": "Internal Server Error"}), 500
