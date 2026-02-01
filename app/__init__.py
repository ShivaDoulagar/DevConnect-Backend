from flask import Flask, send_from_directory
from config import Config
from flask_cors import CORS
from app.extensions import db, migrate, jwt, mail
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)

    # Create uploads folder if it doesn't exist
    # Convert relative path to absolute path based on the backend directory
    upload_folder = app.config["UPLOAD_FOLDER"]
    if not os.path.isabs(upload_folder):
        # Get the backend directory (parent of app directory)
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        upload_folder = os.path.join(backend_dir, upload_folder)
    
    app.config["UPLOAD_FOLDER"] = upload_folder
    os.makedirs(upload_folder, exist_ok=True)

    @app.route("/health")
    def health():
        return {
            "status": "ok",
            "env": app.config["ENV"],
            "db": app.config["SQLALCHEMY_DATABASE_URI"],
        }

    # Serve uploaded profile images
    @app.route("/uploads/profile_images/<filename>")
    def serve_profile_image(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    from app.routes import auth_bp
    from app.routes import user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    return app
