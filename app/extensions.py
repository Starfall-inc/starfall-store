import redis
from flask_sqlalchemy import SQLAlchemy
from flask import current_app
from .Seraphina import Seraphina
from flask_caching import Cache

db = SQLAlchemy()
seraphina = None  # Keep it None initially
redis_clients = {}
cache = None


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


def init_redis(app):
    global seraphina
    """Initializes Redis connections for different database indexes."""
    redis_url = app.config.get("REDIS_URL", "redis://localhost:6379/")
    for db_index in range(5):  # Example: Creating connections for DBs 0 to 4
        redis_clients[db_index] = redis.StrictRedis.from_url(redis_url, db=db_index, decode_responses=True)

    total_database = len(redis_clients)
    seraphina.info(f"Redis connection established for {total_database} databases.")


def init_cache(app):
    global cache
    cache = Cache(app)
