import os
from pathlib import Path

# Base folder for SQLite fallback
basedir = Path(__file__).parent.resolve()

class Config:
    """Base configuration: secret key, DB URI, Auth0, etc."""
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

    # Use DATABASE_URL if set (e.g. in .env), otherwise fall back to local SQLite
    SQLALCHEMY_DATABASE_URI = (
        os.getenv("DATABASE_URL")
        or f"sqlite:///{basedir / 'instance' / 'skaterbater.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session storage
    SESSION_TYPE = "filesystem"

    # Auth0 settings (default callback for local)
    AUTH0_CLIENT_ID     = os.getenv("AUTH0_CLIENT_ID")
    AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
    AUTH0_DOMAIN        = os.getenv("AUTH0_DOMAIN")
    AUTH0_CALLBACK_URL  = os.getenv(
        "AUTH0_CALLBACK_URL",
        "http://localhost:8000/callback"
    )


class ProductionConfig(Config):
    """Production: HTTPS cookies, URL scheme, etc."""
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME  = "https"


class DevelopmentConfig(Config):
    """Development: allow HTTP for convenience."""
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
    PREFERRED_URL_SCHEME  = "http"
