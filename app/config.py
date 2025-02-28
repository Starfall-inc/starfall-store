import os
from dotenv import load_dotenv
from pathlib import Path
import json

# Load environment variables from .env file
load_dotenv()

# Load JSON configuration file
CONFIG_PATH = Path(__file__).parent / "config.json"
with open(CONFIG_PATH, "r") as f:
    config_data = json.load(f)


class Config:
    """Base configuration with default settings"""
    SECRET_KEY = os.getenv("SECRET_KEY", "c4d2e2f68f114b2d8d7a2f3a8e9b1c6f7e8d9f3b6a2c5d4e1a8c9b7d6e1f2a3c")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///database.db")  # Default to SQLite
    DEBUG = False
    LOG_DIR = Path(__file__).parent / "logs"
    MAIN_LOG_FILE = LOG_DIR / "app.log"
    LOG_DIR.mkdir(exist_ok=True)

    # Shop Settings
    SHOP_NAME = config_data["shop"]["name"]
    SHOP_EMAIL = config_data["shop"]["email"]
    SHOP_PHONE = config_data["shop"]["phone"]
    SHOP_ADDRESS = config_data["shop"]["address"]
    CURRENCY = config_data["shop"]["currency"]
    CURRENCY_SYMBOL = config_data["shop"]["currency_symbol"]
    TAX_RATE = config_data["shop"]["tax"]
    SHIPPING_COST = config_data["shop"]["shipping"]
    FREE_SHIPPING_THRESHOLD = config_data["shop"]["free_shipping"]
    LOGO = config_data["shop"]["logo"]
    FAVICON = config_data["shop"]["favicon"]

    # Theme Settings
    PRIMARY_COLOR = config_data["shop"]["theme"]["primary"]
    SECONDARY_COLOR = config_data["shop"]["theme"]["secondary"]
    TEXT_COLOR = config_data["shop"]["theme"]["text"]
    BACKGROUND_COLOR = config_data["shop"]["theme"]["background"]
    DARK_COLOR = config_data["shop"]["theme"]["dark"]


    # Cache Settings :
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300

    # Juspay config :
    # Load Juspay Credentials from Environment Variables
    JUSPAY_MERCHANT_ID = os.getenv("JUSPAY_MERCHANT_ID")
    JUSPAY_API_KEY = os.getenv("JUSPAY_API_KEY")
    JUSPAY_SECRET_KEY = os.getenv("JUSPAY_SECRET_KEY")

    # Juspay API Endpoints
    JUSPAY_ENV = os.getenv("JUSPAY_ENV", "sandbox")  # Default to sandbox
    JUSPAY_BASE_URL = config_data["shop"]["payment"]["sandbox_url"] if JUSPAY_ENV == "sandbox" else config_data["payment"]["production_url"]
    JUSPAY_CALLBACK_PATH = os.getenv("JUSPAY_CALLBACK_PATH", "/api/payment/callback")
    JUSPAY_RETURN_URL = f"{config_data["shop"]["shop_domain"]}{JUSPAY_CALLBACK_PATH}"



class ProductionConfig(Config):
    """Production-specific configuration"""
    ENV = "production"
    DEBUG = False

    # Database Configurations
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@localhost:3306/database")

    # OAuth Configurations
    REDIRECT_URI = os.getenv("REDIRECT_URL")
    OAUTHLIB_INSECURE_TRANSPORT = os.getenv("OAUTHLIB_INSECURE_TRANSPORT", "1")  # Default to enabled


# Configuration dictionary for easy selection
config = {
    "prod": ProductionConfig,
}
