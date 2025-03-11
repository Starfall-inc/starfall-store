import hashlib
from datetime import datetime
from sqlalchemy.orm import joinedload
from app.models.models import Cart, Product, User, db


class CartManager:

    @staticmethod
    def generate_cart_id(user_id):
        """Generates a unique, short human-readable cart ID."""
        unique_seed = f"{user_id}-{datetime.utcnow().timestamp()}"
        short_hash = hashlib.sha1(unique_seed.encode()).hexdigest()[:6]  # 6-character hash
        return f"CART-{short_hash.upper()}"  # Example: CART-A1B2C3

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

            if product.stock_quantity < quantity:
                return {"success": False, "error": "Not enough stock available."}

            # Ensure user has a valid cart ID
            if not user.cart_id:
                user.cart_id = CartManager.generate_cart_id(user_id)

            # Check if the product is already in the cart
            existing_cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()

            if existing_cart_item:
                # Update quantity if product already in cart
                new_quantity = existing_cart_item.quantity + quantity
                if new_quantity > product.stock_quantity:
                    return {"success": False, "error": "Not enough stock to update quantity."}

                existing_cart_item.quantity = new_quantity
                existing_cart_item.updated_at = datetime.utcnow()
            else:
                # Add new item to the cart
                new_cart_item = Cart(
                    cart_id=user.cart_id,  # Associate with user's cart ID
                    user_id=user_id,
                    product_id=product_id,
                    quantity=quantity
                )
                db.session.add(new_cart_item)

            db.session.commit()

            return {
                "success": True,
                "cart_id": user.cart_id,
                "message": "Cart updated." if existing_cart_item else "Item added to cart.",
                "quantity": existing_cart_item.quantity if existing_cart_item else quantity
            }

        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}

    @staticmethod
    def remove_from_cart(user_id, product_id):
        """ Removes a product from the cart. """
        try:
            cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
            if not cart_item:
                return {"success": False, "error": "Item not found in cart."}

            db.session.delete(cart_item)
            db.session.commit()
            return {"success": True, "message": "Item removed from cart."}

        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_cart(user_id):
        """Retrieves all items in a user's cart along with product details."""
        try:
            cart_items = (
                Cart.query
                .filter_by(user_id=user_id)
                .options(joinedload(Cart.product))  # Efficiently loads related product data
                .all()
            )

            return {
                "success": True,
                "cart_id": cart_items[0].cart_id if cart_items else None,
                "items": [
                    {
                        "product_id": item.product.id,
                        "product_name": item.product.name,
                        "product_price": float(item.product.price),
                        "product_image": item.product.images[0].image_url if item.product.images else None,
                        "quantity": item.quantity,
                        "updated_at": item.updated_at
                    }
                    for item in cart_items
                ]
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def clear_cart(user_id):
        """ Clears all items from a user's cart. """
        try:
            Cart.query.filter_by(user_id=user_id).delete()
            db.session.commit()
            return {"success": True, "message": "Cart cleared."}
        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}

    @staticmethod
    def update_cart(user_id, product_id, **kwargs):
        """Updates cart item fields dynamically."""
        try:
            cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
            if not cart_item:
                return {"success": False, "error": "Item not found in cart."}

            product = Product.query.get(product_id)
            if not product:
                return {"success": False, "error": "Product not found."}

            # Check and update fields dynamically
            for key, value in kwargs.items():
                if key == "quantity":
                    if value > product.stock_quantity:
                        return {"success": False, "error": "Not enough stock available."}
                setattr(cart_item, key, value)

            cart_item.updated_at = datetime.utcnow()  # Update timestamp
            db.session.commit()

            return {"success": True, "message": "Cart updated.", "updated_fields": kwargs}

        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": str(e)}
