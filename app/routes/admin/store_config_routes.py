from flask import Blueprint, request, jsonify
from app.modules.Admin.StoreConfigManager import StoreConfigManager  # Ensure this module is correctly imported

admin_api = Blueprint('admin_api', __name__)

@admin_api.route('/store-info', methods=['GET'])
def get_store_info():
    """Get basic store information."""
    return jsonify(StoreConfigManager.get_store_info())

@admin_api.route('/currency', methods=['GET'])
def get_currency():
    """Get store currency settings."""
    return jsonify(StoreConfigManager.get_currency())

@admin_api.route('/theme', methods=['GET'])
def get_theme():
    """Get the store theme settings."""
    return jsonify(StoreConfigManager.get_theme())

@admin_api.route('/theme', methods=['POST'])
def update_theme():
    """Update store theme settings."""
    data = request.json
    response = StoreConfigManager.update_theme(
        primary=data.get("primary"),
        secondary=data.get("secondary"),
        text=data.get("text"),
        background=data.get("background"),
        dark=data.get("dark"),
    )
    return jsonify(response)

@admin_api.route('/payment', methods=['GET'])
def get_payment_provider():
    """Get the payment provider settings."""
    return jsonify(StoreConfigManager.get_payment_provider())

@admin_api.route('/payment', methods=['POST'])
def update_payment_provider():
    """Update payment provider settings."""
    data = request.json
    response = StoreConfigManager.update_payment_provider(
        provider=data.get("provider"),
        sandbox_url=data.get("sandbox_url"),
        production_url=data.get("production_url"),
    )
    return jsonify(response)

@admin_api.route('/update', methods=['POST'])
def update_setting():
    """Update a specific store setting."""
    data = request.json
    key_path = data.get("key_path")
    new_value = data.get("new_value")

    if not key_path:
        return jsonify({"error": "Missing 'key_path' in request"}), 400

    response = StoreConfigManager.update_setting(key_path, new_value)
    return jsonify(response)

@admin_api.route('/reset', methods=['POST'])
def reset_settings():
    """Reset store configuration to default settings."""
    response = StoreConfigManager.reset_to_defaults()
    return jsonify(response)

@admin_api.route('/env/<key>', methods=['GET'])
def get_env_variable(key):
    """Get an environment variable."""
    return jsonify({key: StoreConfigManager.get_env_variable(key)})

@admin_api.route('/env/<key>', methods=['POST'])
def update_env_variable(key):
    """Update an environment variable."""
    data = request.json
    value = data.get("value")

    if not value:
        return jsonify({"error": "Missing 'value' in request"}), 400

    StoreConfigManager.update_env_variable(key, value)
    return jsonify({"success": True, "message": f"Updated '{key}' successfully."})

@admin_api.route('/env/razorpay', methods=['POST'])
def update_razorpay_keys():
    """Update Razorpay API credentials."""
    data = request.json
    StoreConfigManager.update_razorpay_keys(data.get("key_id"), data.get("key_secret"))
    return jsonify({"success": True, "message": "Razorpay keys updated successfully."})

@admin_api.route('/env/google', methods=['POST'])
def update_google_oauth():
    """Update Google OAuth credentials."""
    data = request.json
    StoreConfigManager.update_google_oauth(data.get("client_id"), data.get("client_secret"))
    return jsonify({"success": True, "message": "Google OAuth credentials updated."})

@admin_api.route('/env/facebook', methods=['POST'])
def update_facebook_oauth():
    """Update Facebook OAuth credentials."""
    data = request.json
    StoreConfigManager.update_facebook_oauth(data.get("client_id"), data.get("client_secret"))
    return jsonify({"success": True, "message": "Facebook OAuth credentials updated."})
