from flask_sqlalchemy import SQLAlchemy
from flask import current_app
from .Seraphina import Seraphina

db = SQLAlchemy()
seraphina = None  # Keep it None initially


def init_seraphina(app):
    global seraphina
    seraphina = Seraphina(
        name=app.config["SHOP_NAME"],
        log_file=app.config["MAIN_LOG_FILE"],
        console_output=True,
        max_file_size=10 * 1024 * 1024,
        backup_count=3,
        use_colors=True
    )
    seraphina.info("Seraphina initialized successfully!")
