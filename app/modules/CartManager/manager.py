from app.models import Cart, Product, User, db
from datetime import datetime
import uuid
from sqlalchemy.orm import joinedload



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

            if product.stock_quantity < quantity:
                return {"success": False, "error": "Not enough stock available."}

            # Check if user already has a cart
            existing_cart_item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()

            if existing_cart_item:
                # Update quantity if product already in cart
                new_quantity = existing_cart_item.quantity + quantity
                if new_quantity > product.stock_quantity:
                    return {"success": False, "error": "Not enough stock to update quantity."}

                existing_cart_item.quantity = new_quantity
                existing_cart_item.updated_at = datetime.utcnow()
                db.session.commit()

                return {
                    "success": True,
                    "cart_id": existing_cart_item.id,
                    "message": "Cart updated.",
                    "quantity": new_quantity
                }
            else:
                # Fetch or generate a cart_id
                cart_id = user.cart_id if user.cart_id else str(uuid.uuid4())

                # Create new cart entry
                new_cart_item = Cart(
                    id=cart_id,
                    user_id=user_id,
                    product_id=product_id,
                    quantity=quantity
                )

                # Assign cart_id to user if it's a new cart
                if not user.cart_id:
                    user.cart_id = cart_id

                db.session.add(new_cart_item)
                db.session.commit()

                return {
                    "success": True,
                    "cart_id": cart_id,
                    "message": "Item added to cart.",
                    "quantity": quantity
                }

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
                "cart_id": cart_items[0].id if cart_items else None,
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
