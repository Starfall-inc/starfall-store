from app.models import User
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
from app.utils.hash_utils import hash_password, confirm_password_hash

class CustomerManager:
    @staticmethod
    def create_user(first_name, last_name, email, phone=None, password=None,default_location=None, role="customer", status="active",cart_id=None, auth_provider="manual", profile_pic_url="none"):
        try:
            hashed_password = hash_password(password)
            new_user = User(first_name = first_name, last_name = last_name, password=hashed_password, default_location=default_location, status=status, cart_id=cart_id, auth_provider=auth_provider, profile_pic_url=profile_pic_url)
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            print(f"Error creating customer: {e}")
            # Important: Rollback on error
            db.session.rollback()
            return None
