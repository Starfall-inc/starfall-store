from flask_sqlalchemy import SQLAlchemy
from flask import current_app
from .Seraphina import Seraphina

db = SQLAlchemy()

logger = None  # Initialize as None first

def init_logger():
    """Initialize logger inside an app context."""
    global logger
    print("[DEBUG] Initializing logger...")  # 🟢 Debug message
    logger = Seraphina(
        name="DreamKart",
        log_file=current_app.config['MAIN_LOG_FILE'],
        console_output=True,
        use_colors=True
    )
    print("[DEBUG] Logger initialized successfully.")  # 🟢 Confirm initialization
