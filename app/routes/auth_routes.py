from flask import Blueprint, request, jsonify, redirect, url_for
from app.modules.UserManager import CustomerManager
from app.modules.SessionManager import SessionManager

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["POST"])
def signup():
    """User registration route."""
    data = request.json
    required_fields = ["first_name", "last_name", "email", "password"]

    # Ensure required fields are present
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    user = CustomerManager.create_user(
        first_name=data["first_name"],
        last_name=data["last_name"],
        email=data["email"],
        phone=data.get("phone"),
        password=data["password"]
    )

    if isinstance(user, dict) and "error" in user:
        return jsonify(user), 400

    return jsonify({"success": "User registered successfully"}), 200


@auth_bp.route("/login", methods=["POST"])
def login():
    """User login route."""
    data = request.json
    email = data.get("email")
    password = data.get("password")
    redirect_url = data.get("redirect_url", "/")  # Default redirect after login

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = CustomerManager.get_user_by_email(email)
    if not user or not CustomerManager.confirm_password(email, password):
        return jsonify({"error": "Invalid email or password"}), 401

    # Create session
    session_id = SessionManager.create_session(user.id)

    # Send session ID as a response (or set as a cookie in production)
    response = jsonify({"success": "Login successful", "session_id": session_id, "redirect": redirect_url})
    response.set_cookie("session_id", session_id, httponly=True, secure=True)

    return response
