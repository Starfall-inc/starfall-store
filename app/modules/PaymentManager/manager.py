import hmac
import hashlib
from datetime import datetime
from flask import current_app
from app.extensions import db, seraphina
from app.models.models import Order, PaymentTransaction
import razorpay


class PaymentManager:

    @staticmethod
    def get_razorpay_credentials():
        """Retrieve Razorpay credentials dynamically from Flask config."""
        return {
            "key_id": current_app.config["RAZORPAY_KEY_ID"],
            "key_secret": current_app.config["RAZORPAY_KEY_SECRET"],
        }

    @staticmethod
    def get_razorpay_client():
        """Get initialized Razorpay client."""
        credentials = PaymentManager.get_razorpay_credentials()
        return razorpay.Client(auth=(credentials["key_id"], credentials["key_secret"]))

    @staticmethod
    def initiate_payment(order_id, amount):
        """Creates a payment order with Razorpay."""
        try:
            order = Order.query.get(order_id)
            if not order:
                return {"success": False, "error": "Order not found."}

            # Initialize Razorpay client
            client = PaymentManager.get_razorpay_client()

            # Convert amount to paise (Razorpay uses smallest currency unit)
            amount_in_paise = int(float(amount) * 100)

            # Create Razorpay order
            razorpay_order = client.order.create({
                'amount': amount_in_paise,
                'currency': current_app.config["CURRENCY"],
                'receipt': f'order_{order_id}',
                'notes': {
                    'order_id': str(order_id),
                    'user_id': str(order.user_id)
                }
            })

            if razorpay_order['id']:
                # Return necessary details for frontend integration
                return {
                    "success": True,
                    "order_id": order_id,
                    "razorpay_order_id": razorpay_order['id'],
                    "amount": amount,
                    "currency": current_app.config["CURRENCY"],
                    "key_id": PaymentManager.get_razorpay_credentials()["key_id"]
                }
            else:
                seraphina.error(f"🔴 Failed to create Razorpay order: {razorpay_order}")
                return {"success": False, "error": "Failed to create payment order."}

        except Exception as e:
            seraphina.error(f"🔴 Error initiating Razorpay payment: {str(e)}")
            return {"success": False, "error": "Internal server error"}

    @staticmethod
    def verify_razorpay_signature(order_id, payment_id, signature):
        """Verifies Razorpay signature."""
        try:
            credentials = PaymentManager.get_razorpay_credentials()

            # Generate the signature verification text
            key_secret = credentials["key_secret"]
            generated_signature = hmac.new(
                key_secret.encode(),
                f'{order_id}|{payment_id}'.encode(),
                hashlib.sha256
            ).hexdigest()

            # Verify the signature
            return hmac.compare_digest(generated_signature, signature)

        except Exception as e:
            seraphina.error(f"🔴 Error verifying Razorpay signature: {str(e)}")
            return False

    @staticmethod
    def process_payment_callback(request_data):
        """Handles Razorpay payment callback and updates order status."""
        try:
            razorpay_order_id = request_data.get("razorpay_order_id")
            razorpay_payment_id = request_data.get("razorpay_payment_id")
            razorpay_signature = request_data.get("razorpay_signature")

            # Verify the payment signature
            if not PaymentManager.verify_razorpay_signature(
                    razorpay_order_id, razorpay_payment_id, razorpay_signature
            ):
                return {"success": False, "error": "Invalid payment signature"}

            # Get the Razorpay client and fetch order details
            client = PaymentManager.get_razorpay_client()
            razorpay_order = client.order.fetch(razorpay_order_id)

            # Extract our internal order ID from the notes
            order_id = razorpay_order['notes'].get('order_id')
            if not order_id:
                return {"success": False, "error": "Order not found in Razorpay data"}

            order = Order.query.get(order_id)
            if not order:
                return {"success": False, "error": "Order not found in database"}

            # Get payment details
            payment = client.payment.fetch(razorpay_payment_id)
            amount = float(payment['amount']) / 100  # Convert from paise to main currency
            status = payment['status']
            payment_method = f"{payment.get('method', 'unknown')}"

            # Store payment details
            transaction = PaymentTransaction.query.filter_by(order_id=order_id).first()
            if not transaction:
                transaction = PaymentTransaction(
                    order_id=order_id,
                    transaction_id=razorpay_payment_id,
                    payment_status=status,
                    payment_method=payment_method,
                    amount=amount
                )
                db.session.add(transaction)
            else:
                transaction.payment_status = status
                transaction.payment_method = payment_method
                transaction.updated_at = datetime.utcnow()

            # Update order status based on payment status
            if status == "captured":
                order.status = "pending"
                db.session.commit()
                seraphina.info(f"✅ Payment successful for Order {order_id} via {payment_method}")
                return {"success": True, "message": "Payment successful"}
            else:
                order.status = "Payment Failed"
                db.session.commit()
                seraphina.warn(f"❌ Payment failed for Order {order_id} via {payment_method}")
                return {"success": False, "error": "Payment failed"}

        except Exception as e:
            seraphina.error(f"🔴 Payment Processing Error: {str(e)}")
            return {"success": False, "error": "Internal Server Error"}