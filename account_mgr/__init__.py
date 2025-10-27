import os
import logging
from flask_babel import Babel
from dotenv import load_dotenv
from sqlalchemy import inspect
from flask_mailman import Mail
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from alembic.config import Config
from flask_limiter import Limiter
from flask_migrate import Migrate
from .ansi_ import get_color_support
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from config import DevConfig, ProdConfig
from alembic.script import ScriptDirectory
from flask_limiter.util import get_remote_address
from flask_session import Session as FlaskSession
from werkzeug.exceptions import RequestEntityTooLarge
from alembic.runtime.environment import EnvironmentContext
from flask_login import login_manager, LoginManager, current_user
from flask import Flask, request, redirect, url_for, session, flash
from account_mgr.search.form import TransactionReportForm, CashSummaryForm


load_dotenv()
app = Flask(__name__)


if os.getenv("FLASK_ENV") == "production":
    app.config.from_object(ProdConfig)
else:
    app.config.from_object(DevConfig)


mail = Mail(app)
babel = Babel(app)
cache = Cache(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_message_category = "super_admin_secure.secure_superlogin"

app.config["SESSION_SQLALCHEMY"] = db
flask_session = FlaskSession(app)


logging.basicConfig(level=logging.DEBUG)
colors = get_color_support()


@app.before_request
def middleware():
    """Middleware to handle request path validation and URL canonicalization."""
    if not request.path.startswith("/static"):
        endpoint = request.endpoint or "NO_ENDPOINT"
        print(
            f"{colors['GREEN']}middleware executes before: '{endpoint}' route.{colors['RESET']}"
        )
    try:
        # Check for valid request path format (starts with a slash)
        if not request.path.startswith("/"):
            raise ValueError("Invalid request path format")

        # Skip processing for dynamic routes (non-alphanumeric characters)
        if any(not char.isalnum() for char in request.path[1:]):
            return None

        # URL Canonicalization: Redirect URLs with uppercase letters to lowercase
        if request.path != request.path.lower():
            return redirect(location=request.path.lower())

        # Remove trailing slashes except for root URL
        if request.path != "/" and request.path.endswith("/"):
            return redirect(location=request.path.rstrip("/"))

    except ValueError as e:
        app.logger.error(msg="Middleware error: {e}, Request Path: {request.path}")
        session["error_message"] = (
            f"Middleware error: {e}, Request Path: {request.path}"
        )
        return redirect(url_for(endpoint="errors_.value_error"))

    return None


@app.after_request
def security_headers(response):
    if not request.path.startswith("/static"):
        endpoint = request.endpoint or "NO_ENDPOINT"
        print(
            f"{colors['GREEN']}security header executes before: '{endpoint}' route. {colors['RESET']}"
        )

    # 🔒 Security Headers
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"  # Prevent clickjacking
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )

    # 🔒 Content Security Policy (CSP)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none'; "
        "object-src 'none'; "
        "block-all-mixed-content; "
        "upgrade-insecure-requests; "
        "manifest-src 'self'; "
        "media-src 'self'; "
        "worker-src 'self'; "
        "child-src 'self'; "
        "script-src-attr 'none'; "
        "report-uri /csp-violation-report-endpoint/; "
        "report-to csp-endpoint; "
        # ✅ Scripts
        "script-src 'self' "
        "https://cdn.jsdelivr.net "
        "https://cdnjs.cloudflare.com "
        "https://unpkg.com "
        "https://accounts.google.com "
        "https://apis.google.com; "
        # ✅ Styles
        "style-src 'self' "
        "https://cdn.jsdelivr.net "
        "https://cdnjs.cloudflare.com; "
        # ✅ Fonts
        "font-src 'self' "
        "https://cdnjs.cloudflare.com; "
        # ✅ Images
        "img-src 'self' blob: data:; "
        # ✅ Connections (XHR, fetch, WebSockets, APIs)
        "connect-src 'self' "
        "https://cdn.jsdelivr.net "
        "https://cdnjs.cloudflare.com "
        "https://unpkg.com "
        "https://accounts.google.com "
        "https://apis.google.com; "
    )

    # 🔒 Permissions Policy (disable dangerous APIs by default)
    response.headers["Permissions-Policy"] = (
        "accelerometer=(), "
        "autoplay=(), "
        "camera=(), "
        "display-capture=(), "
        "encrypted-media=(), "
        "fullscreen=(self), "
        "geolocation=(), "
        "gyroscope=(), "
        "magnetometer=(), "
        "microphone=(), "
        "midi=(), "
        "payment=(), "
        "picture-in-picture=(self), "
        "publickey-credentials-get=(), "
        "screen-wake-lock=(), "
        "sync-xhr=(), "
        "usb=(), "
        "xr-spatial-tracking=()"
    )

    return response


limiter = Limiter(
    app=app,
    headers_enabled=True,
    storage_uri="memory://",
    key_func=get_remote_address,
    default_limits=["3000 per hour"],
)


@app.teardown_request
def shutdown_session(exception=None):
    """Teardown function to remove the database session after each request."""
    db.session.remove()


@login_manager.unauthorized_handler
def unauthorized_callback():
    path = request.path

    # Check if trying to access super admin protected routes
    if path.startswith("/super-admin/adashboard/page") or path.startswith(
        "/super-admin/login/page"
    ):
        flash(message="Please log in as Admin to access this page", category="success")

    return redirect(url_for(endpoint="super_admin_secure.secure_superlogin"))


@app.context_processor
def inject_logout_url():
    """Context processor to inject the logout URL into templates."""
    if current_user.is_authenticated and current_user.is_super_admin:
        return dict(
            logout_url=url_for(endpoint="super_admin_secure.super_admin_logout")
        )
    else:
        # Fallback: send to login or home if user is not authenticated or not a super admin
        return dict(logout_url=url_for(endpoint="super_admin_secure.secure_superlogin"))


@app.context_processor
def inject_user_profile_image():
    image_file = None
    if current_user.is_authenticated:
        image_file = url_for("static", filename="media/" + current_user.user_profile)
    return dict(image_file=image_file)


@app.context_processor
def inject_default_forms():
    """Context processor to inject default forms into templates."""
    try:
        # Only allow injection if form data is safe to parse
        if request.method == "GET" or request.content_length < app.config.get(
            "MAX_CONTENT_LENGTH", 10 * 1024 * 1024
        ):
            return {
                "report": TransactionReportForm(),
                "summary_form": CashSummaryForm(),
            }
    except RequestEntityTooLarge:
        # In case request.content_length is already too big
        pass
    except Exception:
        # Catch anything else (just in case)
        pass
    # Return empty so the error page still works
    return {}


""" Importing blueprints and routes from different modules."""
from account_mgr.errors.routes import errors_
from account_mgr.api.routes import meter_cash_api
from account_mgr.media_utils.utils import img_utils
from account_mgr.search.routes import transactions_bp
from account_mgr.account_settings.routes import account_
from account_mgr.super_admin.routes import super_admin_secure
from account_mgr.csa_registration.routes import attendants_registration


# Registering blueprints with the Flask application
app.register_blueprint(errors_, url_prefix="/")
app.register_blueprint(account_, url_prefix="/")
app.register_blueprint(img_utils, url_prefix="/")
app.register_blueprint(meter_cash_api, url_prefix="/")
app.register_blueprint(transactions_bp, url_prefix="/")
app.register_blueprint(super_admin_secure, url_prefix="/")
app.register_blueprint(attendants_registration, url_prefix="/")


from .super_admin.routes import seed_super_admin


# def has_schema_changes(alembic_cfg):
#     """Check if there are pending schema changes (True = needs migrate)."""
#     try:
#         script = ScriptDirectory.from_config(alembic_cfg)

#         def run_migrations(rev, context):
#             diff = context.get_current_revision() != script.get_current_head()
#             return diff

#         with EnvironmentContext(alembic_cfg, script, fn=run_migrations):
#             return run_migrations(None, None)
#     except Exception:
#         # If anything goes wrong, assume we need migration (safe fallback)
#         return True


# def auto_migrate():
#     """Automatically handle migration and upgrade (for Render auto-deploy)."""
#     try:
#         migrations_dir = os.path.join(os.getcwd(), "migrations")

#         # 1️Initialize migrations if folder doesn't exist
#         if not os.path.exists(migrations_dir):
#             os.system("flask db init")
#             logging.info("Flask-Migrate initialized (migrations folder created).")

#         # 2️Prepare Alembic config for direct inspection
#         alembic_cfg_path = os.path.join(migrations_dir, "alembic.ini")
#         if not os.path.exists(alembic_cfg_path):
#             logging.warning("Alembic config missing, skipping diff check.")
#             needs_migrate = True
#         else:
#             alembic_cfg = Config(alembic_cfg_path)
#             needs_migrate = has_schema_changes(alembic_cfg)

#         # 3️Run migrate + upgrade only if needed
#         if needs_migrate:
#             logging.info("🚀 Schema changes detected — applying migrations...")
#             os.system('flask db migrate -m "Auto-migrate (Render)"')
#             os.system("flask db upgrade")
#             logging.info("✅ Database auto-migrated successfully.")
#         else:
#             logging.info("✅ No schema changes detected — skipping migration.")

#     except Exception as e:
#         logging.error(f"❌ Auto migration failed: {e}")


# def init_db():
#     """Initialize database, apply migrations if available, and seed data once."""
#     with app.app_context():
#         try:
#             # --- 1️Auto-migrate on Render (if enabled) ---
#             if os.getenv("AUTO_MIGRATE", "1") == "1":
#                 auto_migrate()

#             # --- 2️Check if database tables exist ---
#             inspector = inspect(db.engine)
#             tables = inspector.get_table_names()

#             if "users" not in tables or "tenants" not in tables:
#                 db.create_all()
#                 logging.info("Tables created successfully.")
#             else:
#                 logging.info("Tables already exist. Skipping create_all().")

#             # --- 3️Always ensure default data is seeded ---
#             seed_super_admin()
#             logging.info("Database seeded successfully (checked or created admin).")

#         except Exception as e:
#             logging.error(f"❌ init_db() failed: {e}")

# ==========================================================

from sqlalchemy import inspect
import os, logging
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.environment import EnvironmentContext

# --- AUTO MIGRATION + DB INIT FIXES ---


def has_schema_changes(alembic_cfg):
    """Check if there are pending schema changes (True = needs migrate)."""
    try:
        script = ScriptDirectory.from_config(alembic_cfg)

        def run_migrations(rev, context):
            diff = context.get_current_revision() != script.get_current_head()
            return diff

        with EnvironmentContext(alembic_cfg, script, fn=run_migrations):
            return run_migrations(None, None)
    except Exception:
        # Safe fallback: assume migration needed if diff check fails
        return True


def auto_migrate():
    """Automatically handle migration and upgrade (for Render auto-deploy)."""
    try:
        migrations_dir = os.path.join(os.getcwd(), "migrations")

        # 1️⃣ Initialize migrations if folder doesn't exist
        if not os.path.exists(migrations_dir):
            os.system("flask db init")
            logging.info("Flask-Migrate initialized (migrations folder created).")

        # ✅ Correct alembic.ini path — it lives at project root
        alembic_cfg_path = os.path.join(os.getcwd(), "alembic.ini")
        if not os.path.exists(alembic_cfg_path):
            logging.warning("Alembic config missing, skipping diff check.")
            needs_migrate = True
        else:
            alembic_cfg = Config(alembic_cfg_path)
            needs_migrate = has_schema_changes(alembic_cfg)

        # 3️⃣ Run migrate + upgrade if needed
        if needs_migrate:
            logging.info("🚀 Schema changes detected — applying migrations...")
            os.system('flask db migrate -m "Auto-migrate (Render)"')
            os.system("flask db upgrade")
            logging.info("✅ Database auto-migrated successfully.")
        else:
            logging.info("✅ No schema changes detected — skipping migration.")

    except Exception as e:
        logging.error(f"❌ Auto migration failed: {e}")


def init_db():
    """Initialize database, apply migrations if available, and seed data once."""
    from .super_admin.routes import seed_super_admin  # ensure local import

    with app.app_context():
        try:
            # --- 1️⃣ Auto-migrate on Render (if enabled) ---
            if os.getenv("AUTO_MIGRATE", "1") == "1":
                auto_migrate()

            # --- 2️⃣ Create tables if they don’t exist ---
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            if "users" not in tables or "tenants" not in tables:
                db.create_all()
                logging.info("Tables created successfully.")
            else:
                logging.info("Tables already exist. Skipping create_all().")

            # --- 3️⃣ Seed default data ---
            seed_super_admin()
            logging.info("Database seeded successfully (checked or created admin).")

        except Exception as e:
            logging.error(f"❌ init_db() failed: {e}")



import sys

if os.getenv("AUTO_MIGRATE", "1") == "1" and not any(
    cmd in sys.argv for cmd in ["db", "shell"]
):
    try:
        with app.app_context():
            init_db()
    except Exception as e:
        app.logger.error(f"❌ Auto DB init failed on startup: {e}")
