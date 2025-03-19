from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models.models import Order, OrderDetail, Product, User
from sqlalchemy import or_
from datetime import datetime, timedelta
import json

# Create a blueprint for order management
order_blueprint = Blueprint('order_api', __name__)


@order_blueprint.route('/', methods=['GET'])
def get_orders():
    """
    Fetch all orders for admin view.
    Returns orders with basic details.
    """
    try:
        # Get all orders sorted by date
        orders = Order.query.order_by(Order.order_place_date.desc()).all()

        # Format order data for response
        order_list = []
        for order in orders:
            # Get customer info
            customer = User.query.get(order.user_id)
            customer_name = f"{customer.first_name} {customer.last_name}" if customer else f"Customer {order.user_id}"
            customer_email = customer.email if customer else None
            customer_phone = customer.phone if customer else None

            # Get order items
            order_items = []
            for detail in order.order_details:
                product = Product.query.get(detail.product_id)
                product_name = product.name if product else f"Product #{detail.product_id}"
                product_image = product.images[0].image_url if product and product.images else None

                order_items.append({
                    "product_id": detail.product_id,
                    "product_name": product_name,
                    "product_image": product_image,
                    "quantity": detail.quantity,
                    "price": float(detail.price),
                    "subtotal": float(detail.subtotal)
                })

            # Calculate order subtotals
            subtotal = sum(item['subtotal'] for item in order_items)
            shipping_cost = float(order.delivery_charges) if order.delivery_charges else 0
            tax = round(subtotal * 0.18, 2)  # Assuming 18% tax, adjust as needed

            order_data = {
                "id": order.id,
                "customer_id": order.user_id,
                "customer_name": customer_name,
                "customer_email": customer_email,
                "customer_phone": customer_phone,
                "order_place_date": order.order_place_date.isoformat(),
                "status": order.status,
                "total": float(order.total),
                "payment_method": order.payment_method,
                "shipping_address": order.shipping_address,
                "shipping_city": "",  # Add these fields if they exist in your model
                "shipping_zip": "",
                "items": order_items,
                "subtotal": subtotal,
                "shipping_cost": shipping_cost,
                "tax": tax
            }
            order_list.append(order_data)

        return jsonify(order_list)

    except Exception as e:
        current_app.logger.error(f"Error fetching orders: {str(e)}")
        return jsonify({"error": "Failed to fetch orders"}), 500


@order_blueprint.route('/<int:order_id>', methods=['GET'])
def get_order_details(order_id):
    """
    Fetch details for a specific order.
    """
    try:
        order = Order.query.get_or_404(order_id)

        # Get customer info
        customer = User.query.get(order.user_id)
        customer_name = f"{customer.first_name} {customer.last_name}" if customer else f"Customer {order.user_id}"
        customer_email = customer.email if customer else None
        customer_phone = customer.phone if customer else None

        # Get order items
        order_items = []
        for detail in order.order_details:
            product = Product.query.get(detail.product_id)
            product_name = product.name if product else f"Product #{detail.product_id}"
            product_image = product.images[0].image_url if product and product.images else None

            order_items.append({
                "product_id": detail.product_id,
                "product_name": product_name,
                "product_image": product_image,
                "quantity": detail.quantity,
                "price": float(detail.price),
                "subtotal": float(detail.subtotal)
            })

        # Calculate order subtotals
        subtotal = sum(item['subtotal'] for item in order_items)
        shipping_cost = float(order.delivery_charges) if order.delivery_charges else 0
        tax = round(subtotal * 0.18, 2)  # Assuming 18% tax, adjust as needed

        order_data = {
            "id": order.id,
            "customer_id": order.user_id,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "customer_phone": customer_phone,
            "order_place_date": order.order_place_date.isoformat(),
            "expected_delivery_date": order.expected_delivery_date.isoformat() if order.expected_delivery_date else None,
            "actual_delivery_date": order.actual_delivery_date.isoformat() if order.actual_delivery_date else None,
            "status": order.status,
            "total": float(order.total),
            "payment_method": order.payment_method,
            "shipping_address": order.shipping_address,
            "shipping_city": "",  # Add these fields if they exist in your model
            "shipping_zip": "",
            "items": order_items,
            "subtotal": subtotal,
            "shipping_cost": shipping_cost,
            "tax": tax,
            "is_completed": order.is_completed
        }

        return jsonify(order_data)

    except Exception as e:
        current_app.logger.error(f"Error fetching order details: {str(e)}")
        return jsonify({"error": "Failed to fetch order details"}), 500


@order_blueprint.route('/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """
    Update the status of an order.
    """
    try:
        order = Order.query.get_or_404(order_id)
        data = request.json

        if not data or 'status' not in data:
            return jsonify({"error": "Status field is required"}), 400

        new_status = data['status']

        # Validate status value
        valid_statuses = ['Pending', 'Shipped', 'Delivered', 'Canceled']
        if new_status not in valid_statuses:
            return jsonify({"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}), 400

        # Update order status
        order.status = new_status

        # Handle status-specific logic
        if new_status == 'Delivered':
            order.actual_delivery_date = datetime.utcnow()
            order.is_completed = True
        elif new_status == 'Shipped':
            # Set expected delivery date to 7 days from now
            order.expected_delivery_date = datetime.utcnow() + timedelta(days=7)

        db.session.commit()

        return jsonify({
            "message": f"Order #{order_id} status updated to {new_status}",
            "order_id": order_id,
            "status": new_status
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating order status: {str(e)}")
        return jsonify({"error": "Failed to update order status"}), 500


@order_blueprint.route('/<int:order_id>/cancel', methods=['PUT'])
def cancel_order(order_id):
    """
    Cancel an order and update inventory.
    """
    try:
        order = Order.query.get_or_404(order_id)

        # Check if order can be canceled
        if order.status == 'Delivered':
            return jsonify({"error": "Cannot cancel an order that has been delivered"}), 400

        # Update order status
        order.status = 'Canceled'

        # Restore inventory for each product
        for detail in order.order_details:
            product = Product.query.get(detail.product_id)
            if product:
                product.stock_quantity += detail.quantity

        db.session.commit()

        return jsonify({
            "message": f"Order #{order_id} has been canceled",
            "order_id": order_id
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error canceling order: {str(e)}")
        return jsonify({"error": "Failed to cancel order"}), 500


@order_blueprint.route('/search', methods=['GET'])
def search_orders():
    """
    Search orders by various criteria.
    """
    try:
        query = request.args.get('query', '')
        status = request.args.get('status', '')

        # Base query
        orders_query = Order.query

        # Apply filters
        if status:
            orders_query = orders_query.filter(Order.status == status)

        if query:
            # Search by order ID, customer info, or total
            orders_query = orders_query.join(User, Order.user_id == User.id, isouter=True).filter(
                or_(
                    Order.id.ilike(f"%{query}%"),
                    User.first_name.ilike(f"%{query}%"),
                    User.last_name.ilike(f"%{query}%"),
                    User.email.ilike(f"%{query}%"),
                    Order.total.ilike(f"%{query}%")
                )
            )

        # Execute query
        orders = orders_query.order_by(Order.order_place_date.desc()).all()

        # Format results
        results = []
        for order in orders:
            customer = User.query.get(order.user_id)
            customer_name = f"{customer.first_name} {customer.last_name}" if customer else f"Customer {order.user_id}"

            results.append({
                "id": order.id,
                "customer_name": customer_name,
                "order_place_date": order.order_place_date.isoformat(),
                "status": order.status,
                "total": float(order.total)
            })

        return jsonify(results)

    except Exception as e:
        current_app.logger.error(f"Error searching orders: {str(e)}")
        return jsonify({"error": "Failed to search orders"}), 500


@order_blueprint.route('/analytics', methods=['GET'])
def get_order_analytics():
    """
    Get analytics data for orders.
    """
    try:
        # Count orders by status
        pending_count = Order.query.filter_by(status='Pending').count()
        shipped_count = Order.query.filter_by(status='Shipped').count()
        delivered_count = Order.query.filter_by(status='Delivered').count()
        canceled_count = Order.query.filter_by(status='Canceled').count()

        # Calculate total revenue
        total_revenue = db.session.query(db.func.sum(Order.total)).filter(Order.status != 'Canceled').scalar() or 0

        # Get recent orders
        recent_orders = Order.query.order_by(Order.order_place_date.desc()).limit(5).all()
        recent_order_data = []

        for order in recent_orders:
            customer = User.query.get(order.user_id)
            customer_name = f"{customer.first_name} {customer.last_name}" if customer else f"Customer {order.user_id}"

            recent_order_data.append({
                "id": order.id,
                "customer_name": customer_name,
                "date": order.order_place_date.isoformat(),
                "total": float(order.total),
                "status": order.status
            })

        return jsonify({
            "counts": {
                "pending": pending_count,
                "shipped": shipped_count,
                "delivered": delivered_count,
                "canceled": canceled_count,
                "total": pending_count + shipped_count + delivered_count + canceled_count
            },
            "revenue": float(total_revenue),
            "recent_orders": recent_order_data
        })

    except Exception as e:
        current_app.logger.error(f"Error getting order analytics: {str(e)}")
        return jsonify({"error": "Failed to get order analytics"}), 500

# Register the blueprint in your Flask app
# In your main app.py file, add:
# from app.blueprints.order_api import order_blueprint
# app.register_blueprint(order_blueprint)