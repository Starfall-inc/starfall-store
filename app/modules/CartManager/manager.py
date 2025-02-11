from app.models import Cart, Product, User, db
from datetime import datetime
import uuid

class CartManager:
    @staticmethod
    def add_to_cart(user_id, product_id, quantity=1):
        """ Adds a product to the cart, updating quantity if it already exists. """
        try:
            user = User.query.get(user_id)
            if not user:
                return {"success": False, "error": "User not found."}

            product = Product.query.get(product_id)
            if not product:
                return {"success": False, "error": "Product not found."}

            existing_cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()

            if existing_cart_item:
                # Update quantity if the product already exists in the cart
                existing_cart_item.quantity += quantity
                existing_cart_item.updated_at = datetime.utcnow()
                db.session.commit()
                return {"success": True, "cart_id": existing_cart_item.id, "message": "Cart updated."}
            else:
                # Create new cart entry
                cart_id = str(uuid.uuid4())  # Generate a unique ID
                new_cart_item = Cart(
                    id=cart_id,
                    user_id=user_id,
                    product_id=product_id,
                    quantity=quantity
                )
                db.session.add(new_cart_item)
                db.session.commit()
                return {"success": True, "cart_id": cart_id, "message": "Item added to cart."}

        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}

    @staticmethod
    def remove_from_cart(user_id, product_id):
        """ Removes a product from the cart. """
        try:
            cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
            if cart_item:
                db.session.delete(cart_item)
                db.session.commit()
                return {"success": True, "message": "Item removed from cart."}
            return {"success": False, "error": "Item not found in cart."}

        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_cart(user_id):
        """ Retrieves all items in a user's cart. """
        try:
            cart_items = Cart.query.filter_by(user_id=user_id).all()
            return [
                {
                    "cart_id": item.id,
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "updated_at": item.updated_at
                }
                for item in cart_items
            ]
        except Exception as e:
            return {"success": False, "error": str(e)}
