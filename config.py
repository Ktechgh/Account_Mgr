import os
from dotenv import load_dotenv

load_dotenv()


# class Config:
#     """Base configuration shared across all environments."""

#     # --- Security & Flask Core ---
#     SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
#     SQLALCHEMY_TRACK_MODIFICATIONS = False

#     # --- Localization ---
#     BABEL_DEFAULT_LOCALE = os.getenv("BABEL_DEFAULT_LOCALE", "en_US")
#     BABEL_DEFAULT_TIMEZONE = os.getenv("BABEL_DEFAULT_TIMEZONE", "UTC")

#     # --- Mail Configuration ---
#     MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
#     MAIL_PORT = int(os.getenv("MAIL_PORT", 465))
#     MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
#     MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
#     MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "True").lower() == "true"
#     MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "False").lower() == "true"

#     # --- Upload & File Configuration ---
#     UPLOAD_FOLDER = os.getenv(
#         "UPLOAD_FOLDER", os.path.abspath("mini_mart/static/media")
#     )
#     MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 10 * 1024 * 1024))  # 10 MB
#     ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".pdf"]

#     # --- Cache Configuration ---
#     CACHE_TYPE = os.getenv("CACHE_TYPE", "simple")
#     CACHE_DEFAULT_TIMEOUT = int(
#         os.getenv("CACHE_DEFAULT_TIMEOUT", 300)
#     )  # 5 min default

#     # --- Session Configuration ---
#     SESSION_TYPE = os.getenv(
#         "SESSION_TYPE", "sqlalchemy"
#     )  # can be 'filesystem' or 'sqlalchemy'
#     SESSION_PERMANENT = os.getenv("SESSION_PERMANENT", "False").lower() == "true"
#     SESSION_USE_SIGNER = True
#     SESSION_KEY_PREFIX = "session:"


class Config:
    """Base configuration shared by all environments."""

    # --- Security ---
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Mail ---
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 465))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "True").lower() == "true"

    # --- File Uploads ---
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".pdf"]
    UPLOAD_FOLDER = os.path.abspath(os.path.join("account_mgr", "static", "media"))

    # --- Cache ----
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 300

    # --- Flask-Session ---
    SESSION_TYPE = "sqlalchemy"
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True
    SESSION_SQLALCHEMY_TABLE = "sessions"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 4
    WTF_CSRF_TIME_LIMIT = 43200


class DevConfig(Config):
    """Development configuration."""

    FLASK_ENV = "development"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL_LOCAL")
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"options": "-c timezone=Africa/Accra"}
    }


class ProdConfig(Config):
    """Production configuration."""

    FLASK_ENV = "production"
    DEBUG = False
    AUTO_MIGRATE = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or os.getenv(
        "DATABASE_URL_INTERNAL"
    )
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"options": "-c timezone=Africa/Accra"}
    }
