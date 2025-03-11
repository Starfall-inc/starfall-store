import redis
from flask_sqlalchemy import SQLAlchemy
from flask import current_app
from authlib.integrations.flask_client import OAuth
from .Seraphina import Seraphina
from flask_caching import Cache

db = SQLAlchemy()
admin_db = SQLAlchemy()  # Admin Database

seraphina = None
redis_clients = {}
cache = None
oauth = OAuth()


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
    redis_url = app.config.get("REDIS_URL", "redis://localhost:6379/")
    for db_index in range(5):
        redis_clients[db_index] = redis.StrictRedis.from_url(redis_url, db=db_index, decode_responses=True)

    seraphina.info(f"Redis connection established for {len(redis_clients)} databases.")


def init_cache(app):
    global cache
    cache = Cache(app)


def init_oauth(app):
    """Initialize OAuth providers dynamically"""

    seraphina.info("Initializing OAuth providers...")

    oauth.init_app(app)

    if app.config.get("GOOGLE_CLIENT_ID"):
        oauth.register(
            name="google",
            client_id=app.config["GOOGLE_CLIENT_ID"],
            client_secret=app.config["GOOGLE_CLIENT_SECRET"],
            access_token_url="https://oauth2.googleapis.com/token",
            authorize_url="https://accounts.google.com/o/oauth2/auth",
            userinfo_endpoint="https://www.googleapis.com/oauth2/v1/userinfo",  # ✅ Correct endpoint
            client_kwargs={"scope": "openid email profile"},
            jwks_uri="https://www.googleapis.com/oauth2/v3/certs"  # ✅ Explicitly set JWKS URI
        )

    if app.config.get("FACEBOOK_CLIENT_ID"):
        oauth.register(
            name="facebook",
            client_id=app.config["FACEBOOK_CLIENT_ID"],
            client_secret=app.config["FACEBOOK_CLIENT_SECRET"],
            access_token_url="https://graph.facebook.com/oauth/access_token",
            authorize_url="https://www.facebook.com/v14.0/dialog/oauth",
            userinfo_endpoint="https://graph.facebook.com/me?fields=id,name,email",
            client_kwargs={"scope": "email"}
        )

    seraphina.info("OAuth providers initialized successfully!")
