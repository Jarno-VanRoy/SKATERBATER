from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(
        host='localhost',
        port=5000,
        debug=True,              # ✅ Enables debug + auto-reload
        use_reloader=True,       # ✅ Force reloader even in direct run
        ssl_context=('certs/cert.pem', 'certs/key.pem')
    )
