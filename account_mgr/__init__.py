import os
import secrets
import logging
from flask_babel import Babel
from dotenv import load_dotenv
from flask_mailman import Mail
from datetime import timedelta
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_limiter import Limiter
from flask_session import Session
from .ansi_ import get_color_support
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from flask_limiter.util import get_remote_address
from werkzeug.exceptions import RequestEntityTooLarge
from flask_login import login_manager, LoginManager, current_user
from flask import Flask, request, redirect, url_for, session, flash
from account_mgr.search.form import TransactionReportForm, CashSummaryForm


app = Flask(__name__)
load_dotenv()


SECRET_KEY = "flask-insecure-c#y(k55srf&7q^i@mi+f*tw_%ll$^w@#cd1=fwa6&8tr^2qwv1"
secret_key = secrets.token_urlsafe(20)  # Generate a secure secret key


APP_DATABASE = os.path.join(os.path.dirname(__file__), "database")
DATABASE_PATH = os.path.join(APP_DATABASE, "account_mgr_db.db")


app.config["SECRET_KEY"] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = (
    os.getenv("DATABASE_URL_LOCAL")  # Try local first
    or os.getenv("DATABASE_URL")  # Then production
    or f"sqlite:///{DATABASE_PATH}"  # Fallback
)


app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["BABEL_DEFAULT_LOCALE"] = "en_US"
app.config["BABEL_DEFAULT_TIMEZONE"] = "UTC"
# app.config["BABEL_DEFAULT_TIMEZONE"] = "Africa/Accra"

if app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgresql"):
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "connect_args": {"options": "-c timezone=Africa/Accra"}
    }


app.config["MAIL_SERVER"] = "smtp.gmail.com"
# app.config["MAIL_PORT"] = 587
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "kennartecht@gmail.com"
app.config["MAIL_PASSWORD"] = "hwnu ujaf aayq kohj"
# app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = True

# Configure media files for file uploads
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB
app.config["ALLOWED_EXTENSIONS"] = [".jpg", ".jpeg", ".png", ".pdf"]
app.config["UPLOAD_FOLDER"] = os.path.abspath(
    os.path.join("mini_mart", "static", "media")
)

app.config["CACHE_TYPE"] = "simple"  # You can use 'simple', 'redis', 'memcached'
app.config["CACHE_DEFAULT_TIMEOUT"] = (
    300  # Cache timeout in seconds (e.g., 300 seconds = 5 minutes)
)

mail = Mail()
mail.init_app(app)
babel = Babel(app)
cache = Cache(app)
cache.init_app(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)  # Protect against Cross-Site Request Forgery (CSRF) attacks
migrate = Migrate(app, db)  # Database migration with Flask-Migrate


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_message_category = "super_admin_secure.secure_superlogin"


@login_manager.unauthorized_handler
def unauthorized_callback():
    path = request.path

    # Check if trying to access super admin protected routes
    if path.startswith("/super-admin/adashboard/page") or path.startswith(
        "/super-admin/login/page"
    ):
        flash(message="Please log in as Admin to access this page", category="success")

    return redirect(url_for(endpoint="super_admin_secure.secure_superlogin"))


# Session configuration
app.config["SESSION_TYPE"] = "sqlalchemy"  # Use SQLAlchemy backend
# app.config["SESSION_TYPE"] = "filesystem"  # Use SQLAlchemy backend
app.config["SESSION_SQLALCHEMY"] = db  # Reference SQLAlchemy instance
app.config["SESSION_SQLALCHEMY_TABLE"] = "sessions"  # Use the Session model
app.config["SESSION_PERMANENT"] = True  # Set to True for persistent sessions
app.config["SESSION_USE_SIGNER"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=4)
# app.config["SESSION_COOKIE_SAMESITE"] = 'None' Enable this config when using https:
# app.config["WTF_CSRF_TIME_LIMIT"] = 43200  # 12 hours
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = False
Session(app)  # Initialize Flask-Session extension


# Set up logging configuration
logging.basicConfig(level=logging.DEBUG)

""" Flask-Limiter Configuration:"""
limiter = Limiter(
    app=app,
    headers_enabled=True,
    storage_uri="memory://",
    key_func=get_remote_address,
    default_limits=["3000 per hour"],
)

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


@app.teardown_request
def shutdown_session(exception=None):
    """Teardown function to remove the database session after each request."""
    db.session.remove()


def flask_db_init():
    """Function to initialize Flask-Migrate and create the migrations folder."""
    migrations_folder = os.path.join(os.getcwd(), "migrations")
    if not os.path.exists(path=migrations_folder):
        os.system(command="flask db init")


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


from flask import current_app


@app.before_request
def apply_database_migrations():
    """Run Alembic migrations automatically (only in development)."""
    if current_app.config.get("ENV") == "development":
        try:
            upgrade()
            print("✅ Database migrations applied successfully.")
        except Exception as e:
            app.logger.exception("Database migration failed: %s", e)
            print(f"⚠️ Database migration skipped or failed: {e}")
