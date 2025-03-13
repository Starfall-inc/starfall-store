from functools import wraps
from flask import request, jsonify, session
from app.models.admin_models import Users

def require_permission(permission_name, action=None):
    """
    Restrict access to users who have the required permission.
    If an action is provided, the user must have that action within the permission.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = session.get("user_id")
            if not user_id:
                return jsonify({"error": "Unauthorized"}), 403

            user = Users.query.get(user_id)
            if not user or not user.has_permission(permission_name, action):
                return jsonify({"error": "Access denied"}), 403

            return func(*args, **kwargs)
        return wrapper
    return decorator
