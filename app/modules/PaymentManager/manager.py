import hmac
import hashlib
import json
import requests
from datetime import datetime
from flask import current_app
from app.extensions import db, seraphina
from app.models import Order, PaymentTransaction


class PaymentManager:

    @staticmethod
    def get_juspay_credentials():
        """Retrieve Juspay credentials dynamically from Flask config."""
        return {
            "merchant_id": current_app.config["JUSPAY_MERCHANT_ID"],
            "api_key": current_app.config["JUSPAY_API_KEY"],
            "secret_key": current_app.config["JUSPAY_SECRET_KEY"],
            "base_url": current_app.config["JUSPAY_BASE_URL"],
            "return_url": current_app.config["JUSPAY_RETURN_URL"],
        }

    @staticmethod
    def initiate_payment(order_id, amount):
        """Creates a payment order with Juspay."""
        try:
            order = Order.query.get(order_id)
            if not order:
                return {"success": False, "error": "Order not found."}

            juspay = PaymentManager.get_juspay_credentials()

            payload = {
                "merchant_id": juspay["merchant_id"],
                "order_id": str(order_id),
                "amount": str(amount),
                "customer_id": str(order.user_id),
                "return_url": juspay["return_url"],
                "payment_page_client_id": juspay["api_key"]
            }

            print(payload)

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Basic {juspay['api_key']}"
            }

            print(headers)

            response = requests.post(f"{juspay['base_url']}/orders", json=payload, headers=headers)

            result = response.json()

            print(result)

            if result.get("status") == "NEW":
                return {"success": True, "payment_url": result.get("payment_links", {}).get("web")}
            else:
                return {"success": False, "error": result.get("error_message", "Payment initiation failed.")}

        except Exception as e:
            seraphina.error(f"🔴 Error initiating Juspay payment: {str(e)}")
            return {"success": False, "error": "Internal server error"}

    @staticmethod
    def verify_juspay_signature(request_data, received_signature):
        """Verifies Juspay signature using HMAC SHA-256."""
        try:
            juspay = PaymentManager.get_juspay_credentials()
            computed_signature = hmac.new(
                juspay["secret_key"].encode(),
                json.dumps(request_data, separators=(',', ':')).encode(),
                hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(computed_signature, received_signature)
        except Exception as e:
            seraphina.error(f"🔴 Error verifying Juspay signature: {str(e)}")
            return False

    @staticmethod
    def process_payment_callback(request_data):
        """Handles Juspay payment callback and updates order status."""
        try:
            order_id = request_data.get("order_id")
            status = request_data.get("status", "").upper()
            transaction_id = request_data.get("txn_id")
            payment_method = request_data.get("payment_method", "UNKNOWN")
            amount = request_data.get("amount", 0.00)

            if not order_id or not transaction_id or not status:
                return {"success": False, "error": "Missing required fields"}

            order = Order.query.get(order_id)
            if not order:
                return {"success": False, "error": "Order not found."}

            # Store payment details
            transaction = PaymentTransaction.query.filter_by(order_id=order_id).first()
            if not transaction:
                transaction = PaymentTransaction(
                    order_id=order_id,
                    transaction_id=transaction_id,
                    payment_status=status,
                    payment_method=payment_method,
                    amount=amount
                )
                db.session.add(transaction)
            else:
                transaction.payment_status = status
                transaction.payment_method = payment_method
                transaction.updated_at = datetime.utcnow()

            # Update order status
            if status == "CHARGED":
                order.status = "Paid"
                order.actual_delivery_date = datetime.utcnow()
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
