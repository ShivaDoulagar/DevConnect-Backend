from datetime import datetime
from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)
    firebase_uid = db.Column(db.String(128), unique=True, nullable=True)
    public_id = db.Column(db.String(50), unique=True)
    bio = db.Column(db.Text, nullable=True)
    profile_image = db.Column(db.String(255), nullable=True)

    username = db.Column(db.String(50), nullable=False, unique=True)
    github_url = db.Column(db.String(255))
    linkedin_url = db.Column(db.String(255))
    website_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    posts = db.relationship("Post", backref="author", lazy=True, cascade="all, delete")
    comments = db.relationship("Comment", backref="user", lazy=True)
    likes = db.relationship("Like", backref="user", lazy=True)
