from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from sqlalchemy import update
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os


def allowed_file(filename):
    """Check if file extension is allowed"""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


user_bp = Blueprint("users", __name__, url_prefix="/user")
from app.models.user import User


@user_bp.route("/me")
@jwt_required()
def userdata():
    try:
        user_id = get_jwt_identity()
        print(user_id)
        data = db.session.query(User).filter(User.public_id == user_id).first()
        if not data:
            return jsonify({"message": "No user found"}), 400
        return jsonify(
            {
                "message": "ok",
                "username": data.username,
                "bio": data.bio,
                "github": data.github_url,
                "linkedin": data.linkedin_url,
                "portfolio": data.website_url,
                "profile_image": data.profile_image,
            }
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Some error has occurred! {e}"}), 500


@user_bp.route("/update/me", methods=["POST"])
@jwt_required()
def update_data():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        user = db.session.query(User).filter(User.public_id == user_id).first()
        if user.username != data["name"]:
            do_exist = (
                db.session.query(User).filter(User.username == data["name"]).first()
            )
            if do_exist:
                return jsonify({"message": "Username is taken"}), 402
        print(user_id)
        stmt = (
            update(User)
            .where(User.public_id == user_id)
            .values(
                username=data["name"],
                bio=data["bio"],
                github_url=data["github"],
                linkedin_url=data["linkedin"],
                website_url=data["portfolio"],
            )
        )
        db.session.execute(stmt)
        db.session.commit()
        if not user:
            return jsonify({"message": "No user found"}), 400
        print(data)
        return jsonify(
            {
                "message": "updated successfully",
            }
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Some error has occurred! {e}"}), 500


@user_bp.route("/me/profile-image", methods=["POST"])
@jwt_required()
def upload_profile_image():
    """Upload user profile image"""
    try:
        if "image" not in request.files:
            return jsonify({"message": "No file provided"}), 400

        file = request.files["image"]
        if file.filename == "":
            return jsonify({"message": "No selected file"}), 400

        if not allowed_file(file.filename):
            return jsonify(
                {"message": "Invalid file type. Allowed: png, jpg, jpeg"}
            ), 400

        user_id = get_jwt_identity()
        user = User.query.filter(User.public_id == user_id).first()
        if not user:
            return jsonify({"message": "User not found"}), 404

        # Delete old profile image if exists
        if user.profile_image:
            # Extract filename from the URL path (e.g., /uploads/profile_images/filename.png)
            old_filename = os.path.basename(user.profile_image)
            old_file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], old_filename)
            if os.path.exists(old_file_path):
                try:
                    os.remove(old_file_path)
                except Exception as e:
                    print(f"Failed to delete old image: {e}")

        # Save new file
        filename = secure_filename(file.filename)
        unique_name = f"{user.public_id}_{filename}"
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)

        file.save(file_path)

        # Update user profile image in database
        user.profile_image = f"/uploads/profile_images/{unique_name}"
        db.session.commit()

        return jsonify(
            {
                "message": "Profile image uploaded successfully",
                "profile_image": user.profile_image,
            }
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Upload failed: {e}"}), 500
