import os
from flask import Flask, session
from app import create_app

# Create the Flask app via your factory
app = create_app()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        debug=(os.getenv("FLASK_ENV", "development") != "production"),
        use_reloader=True
    )
