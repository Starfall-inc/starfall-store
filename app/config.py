import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration with default settings"""
    SECRET_KEY = os.getenv("SECRET_KEY", "c4d2e2f68f114b2d8d7a2f3a8e9b1c6f7e8d9f3b6a2c5d4e1a8c9b7d6e1f2a3c")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///database.db")  # Default to SQLite
    DEBUG = False
    LOG_DIR = Path(__file__).parent / "logs"
    MAIN_LOG_FILE = LOG_DIR / "app.log"
    LOG_DIR.mkdir(exist_ok=True)


class ProductionConfig(Config):
    """Production-specific configuration"""
    ENV = "production"
    DEBUG = False

    # Database Configurations
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@localhost:3306/database")
    MYSQL_SERVER_PORT = os.getenv("MYSQL_SERVER_PORT", "3306")
    MYSQL_DATABASE_NAME = os.getenv("MYSQL_DATABASE_NAME")
    MYSQL_SERVER_USERNAME = os.getenv("MYSQL_SERVER_USERNAME")
    MYSQL_SERVER_PASSWORD = os.getenv("MYSQL_SERVER_PASSWORD")

    # OAuth Configurations
    REDIRECT_URI = os.getenv("REDIRECT_URL")
    OAUTHLIB_INSECURE_TRANSPORT = os.getenv("OAUTHLIB_INSECURE_TRANSPORT", "1")  # Default to enabled

    # NTFY Notification Service
    NTFY_HOST = os.getenv("NTFY_SERVER_ADDRESS")
    NTFY_USER_ID = os.getenv("NTFY_SERVER_USER_ID")
    NTFY_PASSWORD = os.getenv("NTFY_SERVER_PASSWORD")
    NTFY_CHANNEL = os.getenv("NTFY_SERVER_CHANNEL")

    # MongoDB for Analytics
    MONGO_URI = os.getenv("MONGO_URI")


# Configuration dictionary for easy selection
config = {
    "prod": ProductionConfig,
}
