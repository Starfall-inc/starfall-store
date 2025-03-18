from datetime import datetime, timedelta
from app.extensions import db
from app.modules.CartManager.manager import CartManager
from app.models.models import User, Product, Order, OrderDetail, PaymentTransaction
from app.modules.OrderManager import OrderManager


class AdminOrderManager(OrderManager):
    @staticmethod
    def get_all_orders(filters=None):
        """Retrieve all orders with optional filters for admin view."""
        query = Order.query.join(User)

        if filters:
            if "status" in filters:
                query = query.filter(Order.status == filters["status"])
            if "payment_status" in filters:
                query = query.filter(Order.payment_status == filters["payment_status"])
            if "user_id" in filters:
                query = query.filter(Order.user_id == filters["user_id"])
            if "name" in filters:  # Search by name
                query = query.filter(
                    db.or_(
                        User.first_name.ilike(f"%{filters['name']}%"),
                        User.last_name.ilike(f"%{filters['name']}%")
                    )
                )
            if "date_range" in filters:
                start_date, end_date = filters["date_range"]
                query = query.filter(Order.order_place_date.between(start_date, end_date))

        orders = query.order_by(Order.order_place_date.desc()).all()

        return [
            {
                "order_id": order.id,
                "customer": f"{order.user.first_name} {order.user.last_name}",
                "email": order.user.email,
                "total": float(order.total),
                "status": order.status,
                "placed_on": order.order_place_date.strftime("%Y-%m-%d %H:%M:%S"),
                "payment_status": order.payment_status,
                "expected_delivery": order.expected_delivery_date,
                "items_count": len(order.order_details)
            }
            for order in orders
        ]

    @staticmethod
    def create_manual_order(user_id, product_list, shipping_address, payment_method, delivery_charges=0.00):
        """
        Admin can create an order manually.

        product_list = [{"product_id": 1, "quantity": 2}, {"product_id": 3, "quantity": 1}]
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return {"success": False, "error": "User not found."}

            total_amount = 0
            order_details = []

            for item in product_list:
                product = Product.query.get(item["product_id"])
                if not product or product.stock_quantity < item["quantity"]:
                    return {"success": False, "error": f"Insufficient stock for {product.name}"}

                subtotal = product.price * item["quantity"]
                total_amount += subtotal

                order_details.append(
                    OrderDetail(
                        product_id=item["product_id"],
                        quantity=item["quantity"],
                        price=product.price,
                        subtotal=subtotal
                    )
                )

                product.stock_quantity -= item["quantity"]

            total_amount += delivery_charges

            order = Order(
                user_id=user_id,
                total=total_amount,
                shipping_address=shipping_address,
                delivery_charges=delivery_charges,
                payment_method=payment_method,
                expected_delivery_date=datetime.utcnow() + timedelta(days=5),
                status="Processing"
            )

            db.session.add(order)
            for detail in order_details:
                detail.order_id = order.id
                db.session.add(detail)

            db.session.commit()
            return {"success": True, "message": "Manual order created.", "order_id": order.id}

        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_all_refunds():
        """Retrieve all refund requests."""
        refunds = PaymentTransaction.query.filter(PaymentTransaction.payment_status == "refunded").all()

        return [
            {
                "transaction_id": refund.transaction_id,
                "order_id": refund.order_id,
                "customer": f"{refund.order.user.first_name} {refund.order.user.last_name}",
                "amount": refund.amount,
                "payment_method": refund.payment_method,
                "refund_status": refund.payment_status,
                "date": refund.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for refund in refunds
        ]

    @staticmethod
    def bulk_update_orders(order_ids, status):
        """Bulk update the status of multiple orders."""
        try:
            orders = Order.query.filter(Order.id.in_(order_ids)).all()
            for order in orders:
                order.status = status

            db.session.commit()
            return {"success": True, "message": f"Updated {len(orders)} orders to {status}"}

        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}
