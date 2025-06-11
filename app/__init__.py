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
    """Factory function to create and configure the SKATERBATER Flask app."""
    app = Flask(__name__)

    # Load config from project root
    from config import Config
    app.config.from_object(Config)

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    session_manager.init_app(app)

    # Initialize OAuth from separate module to avoid circular import
    from app.oauth import oauth
    oauth.init_app(app)

    # Register main blueprint (after app is ready)
    from .routes import main_bp
    app.register_blueprint(main_bp)

    # Inject logged-in user into all templates
    @app.context_processor
    def inject_user():
        return dict(user=session.get('user'))

    # # ✅ Auto-login as fake user during development
    # if os.getenv("DEBUG_FAKE_LOGIN", "false").lower() == "true":
    #     print("⚠️  DEBUG_FAKE_LOGIN is enabled — all requests use fake user 'auth0|demo_user'")
    #
    #     @app.before_request
    #     def fake_login_for_demo_user():
    #         if "user" not in session:
    #             session["user"] = {
    #                 "sub": "auth0|demo_user",
    #                 "name": "Demo Skater",
    #                 "email": "demo@skaterbater.com"
    #             }

    return app
