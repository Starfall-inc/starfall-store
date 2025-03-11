from flask import Blueprint, request, jsonify, redirect, url_for
from app.modules.UserManager import CustomerManager
from app.modules.SessionManager import SessionManager
from app.extensions import oauth, seraphina

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


@auth_bp.route("/check-session")
def check_session():
    session_id = request.cookies.get("session_id")
    if session_id and SessionManager.get_session(session_id):
        return jsonify({"logged_in": True})
    return jsonify({"logged_in": False})


# ✅ Google OAuth Login
@auth_bp.route("/login/google")
def login_google():
    return oauth.google.authorize_redirect(url_for("auth.google_callback", _external=True))


@auth_bp.route("/login/google/callback")
def google_callback():
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.get("https://www.googleapis.com/oauth2/v2/userinfo").json()

    if not user_info or "email" not in user_info:
        return jsonify({"error": "Google authentication failed"}), 400

    user = CustomerManager.get_user_by_email(user_info["email"])
    if not user:
        user = CustomerManager.create_user(
            first_name=user_info.get("given_name", ""),
            last_name=user_info.get("family_name", ""),
            email=user_info["email"],
            password=None,
            auth_provider="google"
        )

    session_id = SessionManager.create_session(user.id)

    seraphina.info(f"a google User created: {user}")

    response = redirect("/")
    response.set_cookie("session_id", session_id, httponly=True, secure=True)
    return response


# ✅ Facebook OAuth Login
@auth_bp.route("/login/facebook")
def login_facebook():
    return oauth.facebook.authorize_redirect(url_for("auth.facebook_callback", _external=True))


@auth_bp.route("/login/facebook/callback")
def facebook_callback():
    token = oauth.facebook.authorize_access_token()
    user_info = oauth.facebook.get("me?fields=id,name,email").json()

    if not user_info or "email" not in user_info:
        return jsonify({"error": "Facebook authentication failed"}), 400

    user = CustomerManager.get_user_by_email(user_info["email"])
    if not user:
        first_name, last_name = user_info["name"].split(" ", 1)
        user = CustomerManager.create_user(
            first_name=first_name,
            last_name=last_name,
            email=user_info["email"],
            password=None,
            auth_provider="google"
        )

        seraphina.info(f"a facebook User created: {user}")

    session_id = SessionManager.create_session(user.id)

    response = redirect("/")
    response.set_cookie("session_id", session_id, httponly=True, secure=True)
    return response
