from app.models import User
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.extensions import db
from app.utils.hash_utils import hash_password, confirm_password_hash
import logging

logger = logging.getLogger(__name__)


class CustomerManager:
    @staticmethod
    def create_user(first_name, last_name, email, phone=None, password=None, default_location=None,
                    role="customer", status="active", cart_id=None, auth_provider="manual",
                    profile_pic_url="none"):
        try:
            # Check if email already exists
            if User.query.filter_by(email=email).first():
                return {"error": "Email already registered"}

            hashed_password = hash_password(password) if password else None
            new_user = User(
                first_name=first_name, last_name=last_name, email=email, phone=phone,
                password=hashed_password, default_location=default_location, status=status,
                cart_id=cart_id, auth_provider=auth_provider, profile_pic_url=profile_pic_url
            )
            db.session.add(new_user)
            db.session.commit()
            return new_user
        except IntegrityError:
            db.session.rollback()
            return {"error": "Integrity error, possibly duplicate entry"}
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating customer: {e}")
            return {"error": "Internal server error"}

    @staticmethod
    def get_user_by_email(email):
        try:
            return User.query.filter_by(email=email).first()
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None

    @staticmethod
    def get_user_by_id(user_id):
        try:
            return User.query.get(user_id)
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None

    @staticmethod
    def update_user(user_id, **kwargs):
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}

            for key, value in kwargs.items():
                setattr(user, key, value)

            db.session.commit()
            return user
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error updating user: {e}")
            return {"error": "Failed to update user"}

    @staticmethod
    def delete_user(user_id):
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}

            db.session.delete(user)
            db.session.commit()
            return {"success": "User deleted"}
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting user: {e}")
            return {"error": "Failed to delete user"}

    @staticmethod
    def confirm_password(email, password):
        """Checks if the provided password matches the stored password hash."""
        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                return {"error": "User not found"}

            return confirm_password_hash(user.password, password)

        except Exception as e:
            logger.error(f"Error confirming password: {e}")
            return {"error": "Internal server error"}
