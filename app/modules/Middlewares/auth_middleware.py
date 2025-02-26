from functools import wraps
from flask import request, redirect, url_for, jsonify
from urllib.parse import quote
from app.modules.SessionManager.manager import SessionManager


def login_required(func):
    """
    Decorator to check if a user is logged in.
    If not, redirect them to log in with a `redirect` parameter.
    """

    @wraps(func)
    def decorated_function(*args, **kwargs):
        session_id = request.cookies.get("session_id")  # Get session from cookies
        session_data = SessionManager.get_session(session_id) if session_id else None

        if not session_data:  # No valid session
            if request.method == "GET":
                # Use `request.full_path` to include query parameters in redirect
                redirect_url = quote(request.full_path)
                return redirect(url_for('siteroute.render_login_page', redirect=redirect_url))
            elif request.method == "POST":
                return jsonify({"success": False, "error": "Unauthorized access"}), 401

        return func(*args, **kwargs)  # If logged in, proceed with the function

    return decorated_function
