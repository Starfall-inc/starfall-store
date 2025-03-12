from app.models.models import User
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.extensions import db
from app.utils.hash_utils import hash_password, confirm_password_hash
import logging

logger = logging.getLogger(__name__)

class CustomerManager:
    """Manages customer-related operations in the storefront."""

    @staticmethod
    def create_user(first_name, last_name, email, phone=None, password=None, default_location=None,
                    role="customer", status="active", cart_id=None, auth_provider="manual",
                    profile_pic_url="none"):
        """Creates a new customer account."""
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
            return {"success": True, "message": "User created successfully.", "user_id": new_user.id}
        except IntegrityError:
            db.session.rollback()
            return {"error": "Integrity error, possibly duplicate entry"}
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating customer: {e}")
            return {"error": "Internal server error"}

    @staticmethod
    def get_user_by_email(email):
        """Fetch a user by email."""
        try:
            return User.query.filter_by(email=email).first()
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None

    @staticmethod
    def get_user_by_id(user_id):
        """Fetch a user by ID."""
        try:
            return User.query.get(user_id)
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None

    @staticmethod
    def get_all_users(page=1, per_page=10):
        """Fetch all users with pagination."""
        try:
            users = User.query.paginate(page=page, per_page=per_page, error_out=False)
            return {
                "total_users": users.total,
                "users": [
                    {
                        "user_id": user.id,
                        "name": f"{user.first_name} {user.last_name}",
                        "email": user.email,
                        "phone": user.phone,
                        "status": user.status
                    }
                    for user in users.items
                ]
            }
        except Exception as e:
            logger.error(f"Error fetching all users: {e}")
            return {"error": "Internal server error"}

    @staticmethod
    def search_users(query, page=1, per_page=10):
        """Search users by name, email, or phone."""
        try:
            search_term = f"%{query}%"
            users = User.query.filter(
                db.or_(
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term),
                    User.email.ilike(search_term),
                    User.phone.ilike(search_term)
                )
            ).paginate(page=page, per_page=per_page, error_out=False)

            return {
                "total_results": users.total,
                "users": [
                    {
                        "user_id": user.id,
                        "name": f"{user.first_name} {user.last_name}",
                        "email": user.email,
                        "phone": user.phone,
                        "status": user.status
                    }
                    for user in users.items
                ]
            }
        except Exception as e:
            logger.error(f"Error searching users: {e}")
            return {"error": "Internal server error"}

    @staticmethod
    def update_user(user_id, **kwargs):
        """Update user details."""
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}

            for key, value in kwargs.items():
                setattr(user, key, value)

            db.session.commit()
            return {"success": True, "message": "User updated successfully."}

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error updating user: {e}")
            return {"error": "Failed to update user"}

    @staticmethod
    def soft_delete_user(user_id):
        """Soft delete a user by marking them as inactive instead of deleting."""
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}

            user.status = "inactive"
            db.session.commit()
            return {"success": True, "message": "User deactivated successfully."}

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error soft deleting user: {e}")
            return {"error": "Failed to deactivate user"}

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

    @staticmethod
    def reset_password(user_id, new_password):
        """Resets a user's password."""
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}

            user.password = hash_password(new_password)
            db.session.commit()
            return {"success": True, "message": "Password reset successfully."}

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error resetting password: {e}")
            return {"error": "Failed to reset password"}

    @staticmethod
    def verify_user_email(email):
        """Marks a user's email as verified."""
        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                return {"error": "User not found"}

            user.email_verified = True
            db.session.commit()
            return {"success": True, "message": "Email verified successfully."}

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error verifying user email: {e}")
            return {"error": "Failed to verify email"}

    @staticmethod
    def get_active_users():
        """Fetch all active users."""
        try:
            users = User.query.filter_by(status="active").all()
            return [
                {
                    "user_id": user.id,
                    "name": f"{user.first_name} {user.last_name}",
                    "email": user.email,
                    "phone": user.phone
                }
                for user in users
            ]
        except Exception as e:
            logger.error(f"Error fetching active users: {e}")
            return {"error": "Internal server error"}

    @staticmethod
    def admin_suspend_user(user_id):
        """Admin suspends a user (temporarily deactivates)."""
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}

            user.status = "suspended"
            db.session.commit()
            return {"success": True, "message": "User suspended successfully."}

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error suspending user: {e}")
            return {"error": "Failed to suspend user"}

    @staticmethod
    def admin_activate_user(user_id):
        """Admin activates a suspended user."""
        try:
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}

            user.status = "active"
            db.session.commit()
            return {"success": True, "message": "User activated successfully."}

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error activating user: {e}")
            return {"error": "Failed to activate user"}
