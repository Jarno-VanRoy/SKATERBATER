import os

# Get the absolute path to the directory where this file lives
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration for the SKATERBATER app."""

    # Flask secret key from .env
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

    # SQLite database - stored in project root for convenience
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "instance", "skaterbater.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Session will store session data on the local filesystem
    SESSION_TYPE = "filesystem"

    # Auth0 configuration (loaded from .env)
    AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
    AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
    AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
    AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL")
