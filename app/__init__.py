import os
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
session_manager = Session()

def create_app():
    app = Flask(__name__)

    # ─── Pick your config class based on FLASK_ENV ───────────────────
    if os.getenv("FLASK_ENV", "development") == "production":
        from config import ProductionConfig as ActiveConfig
    else:
        from config import DevelopmentConfig as ActiveConfig

    app.config.from_object(ActiveConfig)

    # ─── Initialize extensions ───────────────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)
    session_manager.init_app(app)

    # ─── OAuth setup ────────────────────────────────────────────────
    from app.oauth import oauth
    oauth.init_app(app)

    # ─── Register your blueprint(s) ─────────────────────────────────
    from .routes import main_bp
    app.register_blueprint(main_bp)

    # ─── Make `user` available in all templates ─────────────────────
    @app.context_processor
    def inject_user():
        return dict(user=session.get("user"))

    return app
