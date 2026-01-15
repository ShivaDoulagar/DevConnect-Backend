from flask import Flask, redirect, url_for, render_template, request, jsonify
from config import Config
from flask_cors import CORS
from app.extensions import db, migrate, jwt, mail
from app.models.user import User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)

    @app.route("/health")
    def health():
        return {
            "status": "ok",
            "env": app.config["ENV"],
            "db": app.config["SQLALCHEMY_DATABASE_URI"],
        }

    from app.routes import auth_bp

    app.register_blueprint(auth_bp)

    return app
