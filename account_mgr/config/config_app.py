import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "default-secret-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BABEL_DEFAULT_LOCALE = "en_US"
    # Optional, only for Flask-Babel formatting
    # BABEL_DEFAULT_TIMEZONE = "Africa/Accra"

class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://postgres:p4ssw0rd@localhost:5432/mini_mart_pos"
    )
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {'options': '-c timezone=Africa/Accra'}
    }

class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {'options': '-c timezone=Africa/Accra'}
    }

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"




# NOTE:
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import DevConfig, ProdConfig, TestConfig

db = SQLAlchemy()

def create_app(env="dev"):
    app = Flask(__name__)
    
    if env == "dev":
        app.config.from_object(DevConfig)
    elif env == "prod":
        app.config.from_object(ProdConfig)
    elif env == "test":
        app.config.from_object(TestConfig)
    else:
        raise ValueError("Invalid environment config")

    db.init_app(app)
    return app


# NOTE:
# from your_app import create_app

app = create_app(env="dev")  # or "prod" or "test"

if __name__ == "__main__":
    app.run(debug=True)
