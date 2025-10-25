import os
from account_mgr import app, init_db

# if __name__ == "__main__":
#     if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
#         init_db()
#     app.run(debug=True)


# if __name__ == "__main__":
#     init_db()
#     app.run(debug=True)


if __name__ == "__main__":
    # Ensure auto-migrate and seeding run in Render too
    with app.app_context():
        print("🚀 Running database initialization (Render startup)...")
        init_db()

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
else:
    # For Render’s Gunicorn entry point
    with app.app_context():
        print("🚀 Running database initialization (Gunicorn startup)...")
        init_db()
