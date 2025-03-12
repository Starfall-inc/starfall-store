import razorpay
from datetime import datetime
from flask import current_app
from app.extensions import db, seraphina
from app.models.models import PaymentTransaction, Order, User


class PaymentManager:

    @staticmethod
    def get_razorpay_client():
        """Get initialized Razorpay client."""
        return razorpay.Client(auth=(
            current_app.config["RAZORPAY_KEY_ID"],
            current_app.config["RAZORPAY_KEY_SECRET"]
        ))

    @staticmethod
    def process_refund(payment_id, amount=None, notes=None):
        """
        Processes a refund via Razorpay and updates the transaction.

        Args:
            payment_id (str): The Razorpay payment ID.
            amount (float, optional): The amount to refund (INR). If None, full refund.
            notes (dict, optional): Additional refund details.

        Returns:
            dict: Refund result.
        """
        try:
            client = PaymentManager.get_razorpay_client()
            transaction = PaymentTransaction.query.filter_by(transaction_id=payment_id).first()

            if not transaction:
                return {"success": False, "error": "Transaction not found."}

            # Convert amount to paise (Razorpay uses the smallest currency unit)
            data = {}
            if amount:
                data["amount"] = int(amount * 100)
            if notes:
                data["notes"] = notes

            # Create the refund
            refund = client.refunds.create(payment_id, data=data)

            if refund.get("id"):
                # Update transaction status in the database
                transaction.payment_status = "refunded"
                transaction.updated_at = datetime.utcnow()
                db.session.commit()

                # Log the refund action
                seraphina.info(f"🔄 Refund processed for transaction {payment_id}, Refund ID: {refund['id']}")

                return {"success": True, "message": "Refund successful", "refund_details": refund}
            else:
                seraphina.error(f"🔴 Refund failed for {payment_id}: {refund}")
                return {"success": False, "error": "Refund failed"}

        except Exception as e:
            seraphina.error(f"🔴 Error processing refund: {str(e)}")
            return {"success": False, "error": "Internal server error"}

    @staticmethod
    def get_all_transactions(filters=None):
        """Retrieve all payment transactions with optional filters."""
        query = PaymentTransaction.query.join(Order).join(User)  # Ensure proper joins

        # Apply filters dynamically
        if filters:
            if "status" in filters:
                query = query.filter_by(payment_status=filters["status"])
            if "payment_method" in filters:
                query = query.filter_by(payment_method=filters["payment_method"])
            if "order_id" in filters:
                query = query.filter_by(order_id=filters["order_id"])
            if "user_id" in filters:
                query = query.filter(Order.user_id == filters["user_id"])
            if "date_range" in filters:
                start_date, end_date = filters["date_range"]
                query = query.filter(PaymentTransaction.created_at.between(start_date, end_date))

        transactions = query.order_by(PaymentTransaction.created_at.desc()).all()

        return [
            {
                "transaction_id": txn.transaction_id,
                "order_id": txn.order_id,
                "account_name": f"{txn.order.user.first_name} {txn.order.user.last_name}" if txn.order.user else "Unknown",
                "amount": txn.amount,
                "payment_method": txn.payment_method,
                "status": txn.payment_status,
                "date": txn.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for txn in transactions
        ]


    @staticmethod
    def get_payment_dashboard_metrics():
        """Returns key payment statistics for the admin dashboard."""
        total_revenue = db.session.query(db.func.sum(PaymentTransaction.amount)).filter_by(
            payment_status="captured").scalar() or 0
        total_refunded = db.session.query(db.func.sum(PaymentTransaction.amount)).filter_by(
            payment_status="refunded").scalar() or 0
        pending_payments = PaymentTransaction.query.filter_by(payment_status="pending").count()
        failed_payments = PaymentTransaction.query.filter_by(payment_status="failed").count()

        return {
            "total_revenue": total_revenue,
            "total_refunded": total_refunded,
            "pending_payments": pending_payments,
            "failed_payments": failed_payments
        }
