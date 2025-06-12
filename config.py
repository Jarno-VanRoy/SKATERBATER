import os

# absolute path to project root
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration for the SKATERBATER app."""

    # Flask secret key from .env
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

    # Database URL (e.g., Postgres on Render or local SQLite)
    SQLALCHEMY_DATABASE_URI = (
            os.getenv("SQLALCHEMY_DATABASE_URI")
            or "sqlite:///" + os.path.join(basedir, "instance", "skaterbater.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Session will store session data on the local filesystem
    SESSION_TYPE = "filesystem"

    # Auth0 configuration (loaded from .env)
    AUTH0_CLIENT_ID     = os.getenv("AUTH0_CLIENT_ID")
    AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
    AUTH0_DOMAIN        = os.getenv("AUTH0_DOMAIN")
    AUTH0_CALLBACK_URL  = os.getenv("AUTH0_CALLBACK_URL")


class ProductionConfig(Config):
    """Production-specific configuration."""

    # Ensure cookies are only sent over HTTPS
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

    # Generate external URLs with https://
    PREFERRED_URL_SCHEME = "https"


class DevelopmentConfig(Config):
    """Development-specific configuration."""
    # In development, allow HTTP for convenience
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
    PREFERRED_URL_SCHEME = "http"
