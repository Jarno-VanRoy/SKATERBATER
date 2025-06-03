from app import create_app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(
        host='localhost',
        port=5000,
        debug=True,              # ✅ Enables auto-reload on code change
        use_reloader=True,       # ✅ Force reload even on direct runs
        ssl_context=('certs/cert.pem', 'certs/key.pem')  # 🔐 Local HTTPS certs
    )
