# # import os
# from account_mgr import app, init_db


# if __name__ == "__main__":
#     init_db()

#     # app.run(debug=True)
#     app.run(debug=True, host='0.0.0.0', port=4000)


import os
import logging
from account_mgr import app



def run_auto_migrate():
    """Safely apply database migrations on Render startup."""
    try:
        with app.app_context():
            logging.info("🚀 Running flask db upgrade (auto-migrate)")
            os.system("flask db upgrade")
            logging.info("✅ Database upgrade complete.")
    except Exception as e:
        logging.error(f"❌ Auto migration failed: {e}")


if __name__ == "__main__":
    # Auto-migrate only on Render runtime
    if os.getenv("RENDER", "0") == "1":
        run_auto_migrate()

    app.run(debug=True)
