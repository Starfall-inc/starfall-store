import json
import os
from pathlib import Path
import logging

from dotenv import set_key

logger = logging.getLogger(__name__)

class StoreConfigManager:
    """Handles loading, modifying, and saving store configuration."""

    CONFIG_FILE = Path(__file__).parent / "configuration.json"
    ENV_PATH = Path(__file__).parent.parent / ".env"  # Adjust path if needed

    @staticmethod
    def load_config():
        """Loads the configuration from JSON file."""
        try:
            with open(StoreConfigManager.CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("⚠️ Configuration file not found.")
            return {"error": "Configuration file missing"}
        except json.JSONDecodeError:
            logger.error("⚠️ Error parsing configuration file.")
            return {"error": "Invalid configuration file"}

    @staticmethod
    def get_setting(key_path, default=None):
        """
        Retrieves a specific setting from the config.

        Args:
            key_path (str): Dot-separated key path (e.g., "shop.currency").
            default (any): Default value if key is not found.

        Returns:
            Any: The value of the setting or default.
        """
        config = StoreConfigManager.load_config()
        keys = key_path.split(".")
        value = config

        try:
            for key in keys:
                value = value[key]
            return value
        except KeyError:
            logger.warning(f"⚠️ Setting '{key_path}' not found. Returning default: {default}")
            return default

    @staticmethod
    def update_setting(key_path, new_value):
        """
        Updates a specific setting in the configuration.

        Args:
            key_path (str): Dot-separated key path (e.g., "shop.currency").
            new_value (any): New value to set.

        Returns:
            dict: Success or error message.
        """
        config = StoreConfigManager.load_config()
        keys = key_path.split(".")
        value = config

        try:
            for key in keys[:-1]:
                value = value[key]

            value[keys[-1]] = new_value

            # Save the updated configuration
            StoreConfigManager.save_config(config)

            return {"success": True, "message": f"Updated '{key_path}' successfully."}
        except KeyError:
            return {"error": f"Invalid key path: {key_path}"}

    @staticmethod
    def save_config(config):
        """Saves the modified configuration to the file."""
        try:
            with open(StoreConfigManager.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            return {"success": True, "message": "Configuration saved successfully."}
        except Exception as e:
            logger.error(f"⚠️ Error saving configuration: {e}")
            return {"error": "Failed to save configuration"}

    @staticmethod
    def get_store_info():
        """Returns store basic information."""
        config = StoreConfigManager.load_config()
        return {
            "name": config["shop"]["name"],
            "email": config["shop"]["email"],
            "phone": config["shop"]["phone"],
            "address": config["shop"]["address"],
            "domain": config["shop"]["shop_domain"]
        }

    @staticmethod
    def get_currency():
        """Returns the store currency settings."""
        return {
            "currency": StoreConfigManager.get_setting("shop.currency"),
            "symbol": StoreConfigManager.get_setting("shop.currency_symbol")
        }

    @staticmethod
    def get_theme():
        """Returns the current store theme settings."""
        return StoreConfigManager.get_setting("shop.theme", {})

    @staticmethod
    def update_theme(primary=None, secondary=None, text=None, background=None, dark=None):
        """Updates theme settings dynamically."""
        current_theme = StoreConfigManager.get_theme()

        # Update only provided colors
        if primary:
            current_theme["primary"] = primary
        if secondary:
            current_theme["secondary"] = secondary
        if text:
            current_theme["text"] = text
        if background:
            current_theme["background"] = background
        if dark:
            current_theme["dark"] = dark

        return StoreConfigManager.update_setting("shop.theme", current_theme)

    @staticmethod
    def get_payment_provider():
        """Returns the payment provider settings."""
        return StoreConfigManager.get_setting("shop.payment", {})

    @staticmethod
    def update_payment_provider(provider, sandbox_url, production_url):
        """Updates the payment provider settings."""
        new_payment_config = {
            "provider": provider,
            "sandbox_url": sandbox_url,
            "production_url": production_url
        }
        return StoreConfigManager.update_setting("shop.payment", new_payment_config)

    @staticmethod
    def reset_to_defaults():
        """Resets the configuration to default values (backup required)."""
        try:
            default_config = {
                "shop": {
                    "shop_domain": "https://sakuramart-dev.sangonomiya.icu",
                    "name": "SakuraMart",
                    "email": "support@sakuramart.jp",
                    "phone": "098-765-4321",
                    "address": "123 Sakura St, Tokyo, Japan, 100-0001",
                    "currency": "INR",
                    "currency_symbol": "₹",
                    "tax": 0.08,
                    "shipping": 500,
                    "free_shipping": 5000,
                    "logo": "sakura-logo.png",
                    "favicon": "sakura-favicon.ico",
                    "theme": {
                        "primary": "#FFB7C5",
                        "secondary": "#FF69B4",
                        "text": "#4A4A4A",
                        "background": "#FFF0F5",
                        "dark": "#8B0000"
                    },
                    "payment": {
                        "provider": "razorpay",
                        "sandbox_url": "https://api.razorpay.com/v1/",
                        "production_url": "https://api.razorpay.com/v1/"
                    }
                }
            }
            StoreConfigManager.save_config(default_config)
            return {"success": True, "message": "Configuration reset to default."}
        except Exception as e:
            return {"error": f"Failed to reset configuration: {e}"}
    # =========================== 🔹 ENV MANAGEMENT 🔹 ===========================

    @staticmethod
    def get_env_variable(key, default=None):
        """Retrieve a specific environment variable."""
        return os.getenv(key, default)

    @staticmethod
    def update_env_variable(key, value):
        """Update a specific environment variable in the .env file."""
        try:
            set_key(str(StoreConfigManager.ENV_PATH), key, value)
            print(f"✅ Updated .env variable '{key}' to: {value}")
        except Exception as e:
            print(f"❌ Error updating .env variable '{key}': {e}")

    @staticmethod
    def update_razorpay_keys(key_id, key_secret):
        """Update Razorpay API credentials."""
        StoreConfigManager.update_env_variable("RAZORPAY_KEY_ID", key_id)
        StoreConfigManager.update_env_variable("RAZORPAY_KEY_SECRET", key_secret)

    @staticmethod
    def update_google_oauth(client_id, client_secret):
        """Update Google OAuth credentials."""
        StoreConfigManager.update_env_variable("GOOGLE_CLIENT_ID", client_id)
        StoreConfigManager.update_env_variable("GOOGLE_CLIENT_SECRET", client_secret)

    @staticmethod
    def update_facebook_oauth(client_id, client_secret):
        """Update Facebook OAuth credentials."""
        StoreConfigManager.update_env_variable("FACEBOOK_CLIENT_ID", client_id)
        StoreConfigManager.update_env_variable("FACEBOOK_CLIENT_SECRET", client_secret)