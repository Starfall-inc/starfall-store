from datetime import datetime, timedelta
from app.extensions import db
from app.modules.CartManager.manager import CartManager
from app.models.models import User, Product, Order, OrderDetail


class OrderManager:

    @staticmethod
    def place_order(user_id, shipping_address, delivery_charges=0.00):
        """Creates an order from cart items, processes payment, and updates stock."""
        try:
            user = User.query.get(user_id)
            if not user:
                return {"success": False, "error": "User not found."}

            # Retrieve user's cart items
            cart_items = CartManager.get_cart(user_id)["items"]
            if not cart_items:
                return {"success": False, "error": "Cart is empty."}

            # Calculate total cost
            total_amount = sum(item["product_price"] * item["quantity"] for item in cart_items) + delivery_charges

            # Create order entry
            order = Order(
                user_id=user_id,
                total=total_amount,
                shipping_address=shipping_address,
                delivery_charges=delivery_charges,
                status="unpaid",
                expected_delivery_date=datetime.utcnow() + timedelta(days=5)  # Estimate 5-day delivery
            )

            db.session.add(order)
            db.session.flush()  # Get order ID before inserting details

            # Add order details and update stock
            for item in cart_items:
                product = Product.query.get(item["product_id"])
                if not product or product.stock_quantity < item["quantity"]:
                    return {"success": False, "error": f"Stock unavailable for {item['product_name']}"}

                order_detail = OrderDetail(
                    order_id=order.id,
                    product_id=item["product_id"],
                    quantity=item["quantity"],
                    price=item["product_price"],
                    subtotal=item["product_price"] * item["quantity"]
                )
                db.session.add(order_detail)

                # Deduct stock
                product.stock_quantity -= item["quantity"]

            # Clear user's cart after placing order
            CartManager.clear_cart(user_id)

            db.session.commit()
            return {"success": True, "message": "Order placed successfully.", "order_id": order.id}

        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_orders(user_id=None, order_id=None):
        """
        Fetches orders by user_id or order_id.

        If user_id is provided, fetches all orders for that user.
        If order_id is provided, fetches the specific order.
        If neither is provided, returns an error.
        """
        try:
            if user_id:
                user = User.query.get(user_id)
                if not user:
                    return {"success": False, "error": "User not found."}

                orders = Order.query.filter_by(user_id=user_id).all()
                return {
                    "success": True,
                    "orders": [
                        {
                            "order_id": order.id,
                            "total": float(order.total),
                            "status": order.status,
                            "placed_on": order.order_place_date,
                            "payment_method": order.payment_method,
                            "expected_delivery": order.expected_delivery_date,
                            "items": [
                                {
                                    "product_id": detail.product.id,
                                    "product_name": detail.product.name,
                                    "product_image": detail.product.images[0].image_url if detail.product.images else None, #Corrected Line
                                    "quantity": detail.quantity,
                                    "price": float(detail.price),
                                    "subtotal": detail.subtotal
                                }
                                for detail in order.order_details
                            ]
                        }
                        for order in orders
                    ]
                }

            elif order_id:
                order = Order.query.get(order_id)
                if not order:
                    return {"success": False, "error": "Order not found."}

                return {
                    "success": True,
                    "orders": [
                        {
                            "order_id": order.id,
                            "total": float(order.total),
                            "status": order.status,
                            "placed_on": order.order_place_date,
                            "payment_method": order.payment_method,
                            "expected_delivery": order.expected_delivery_date,
                            "items": [
                                {
                                    "product_id": detail.product.id,
                                    "product_name": detail.product.name,
                                    "product_image": detail.product.images[0].image_url if detail.product.images else None, #Corrected Line
                                    "quantity": detail.quantity,
                                    "price": float(detail.price),
                                    "subtotal": detail.subtotal
                                }
                                for detail in order.order_details
                            ]
                        }
                    ]
                }

            else:
                return {"success": False, "error": "Either user_id or order_id must be provided."}

        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def update_order_status(order_id, status, payment_method=None):
        """Updates the status of an order."""
        try:
            order = Order.query.get(order_id)
            if not order:
                return {"success": False, "error": "Order not found."}

            order.status = status
            if payment_method is not None:
                order.payment_method = payment_method
            db.session.commit()
            return {"success": True, "message": "Order status updated successfully."}

        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}

    @staticmethod
    def cancel_order(order_id):
        """Cancels an order and restores stock."""
        try:
            order = Order.query.get(order_id)
            if not order:
                return {"success": False, "error": "Order not found."}

            if order.status == "shipped" or order.status == "delivered":
                return {"success": False, "error": "Order cannot be canceled after shipping."}

            # Restore product stock
            for detail in order.order_details:
                product = Product.query.get(detail.product_id)
                if product:
                    product.stock_quantity += detail.quantity

            db.session.delete(order)
            db.session.commit()
            return {"success": True, "message": "Order canceled and stock restored."}

        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}
