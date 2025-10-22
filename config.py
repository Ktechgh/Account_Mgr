import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "default-secret-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BABEL_DEFAULT_LOCALE = "en_US"
    # Optional for timezone formatting:
    # BABEL_DEFAULT_TIMEZONE = "Africa/Accra"


class DevConfig(Config):
    ENV = "development"
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://postgres:p4ssw0rd@localhost:5432/mini_mart_pos"
    )
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"options": "-c timezone=Africa/Accra"}
    }


class ProdConfig(Config):
    ENV = "production"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"options": "-c timezone=Africa/Accra"}
    }


class TestConfig(Config):
    ENV = "testing"
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
