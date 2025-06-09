import os

# absolute path to project root
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration for the SKATERBATER app."""

    # Flask secret key from .env
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

    # ◾ DATABASE URI
    # First try the env var (e.g. postgresql://user:pass@db:5432/dbname),
    # otherwise fall back to SQLite in instance/
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "sqlite:///" + os.path.join(basedir, "instance", "skaterbater.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Session will store session data on the local filesystem
    SESSION_TYPE = "filesystem"

    # Auth0 configuration (loaded from .env)
    AUTH0_CLIENT_ID     = os.getenv("AUTH0_CLIENT_ID")
    AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
    AUTH0_DOMAIN        = os.getenv("AUTH0_DOMAIN")
    AUTH0_CALLBACK_URL  = os.getenv("AUTH0_CALLBACK_URL")
