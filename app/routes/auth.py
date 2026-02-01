from flask import Blueprint, request, jsonify
from app.models.user import User
import bcrypt
from app.extensions import db
import uuid
from app.extensions import jwt
from config import Config
from datetime import datetime, timezone, timedelta
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/sign", methods=["POST"])
def sign():
    try:
        data = request.get_json()
        user = db.session.query(User).filter(User.email == data["email"]).first()
        if user:
            password = data["password"].encode("utf-8")
            if bcrypt.checkpw(password, user.password_hash.encode("utf-8")):
                # Use create_access_token instead of jwt.encode
                token = create_access_token(
                    identity=user.public_id,
                    expires_delta=timedelta(hours=1),
                )
                return jsonify(
                    {
                        "message": "Sign in successful",
                        "token": token,
                        "username": user.username,
                    }
                )
            else:
                return jsonify({"message": "Invalid password"}), 401
        else:
            return jsonify({"message": "User not found"}), 404
    except Exception as e:
        print(e)
        return jsonify({"message": f"Some error has occurred! {e}"}), 500


@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        if check_user(data["email"]):
            return jsonify({"message": "User already exists!"})
        password = data["password"].encode("utf-8")
        salt = bcrypt.gensalt(rounds=12)
        hashed_password = bcrypt.hashpw(password, salt)
        new_user = User(
            email=data["email"],
            username=data["name"],
            public_id=str(uuid.uuid4()),
            password_hash=hashed_password.decode("utf-8"),
        )
        db.session.add(new_user)
        db.session.commit()
        response = {"message": "User registered successfully"}
        return jsonify(response)
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Some error has occurred! {e}"}), 500


def check_user(mail):
    user = db.session.query(User).filter(User.email == mail).first()
    if user:
        return True
    return False
