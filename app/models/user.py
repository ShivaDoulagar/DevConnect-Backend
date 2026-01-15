from datetime import datetime
from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)
    firebase_uid = db.Column(db.String(128), unique=True, nullable=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(100))
    bio = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
