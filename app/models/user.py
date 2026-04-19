from app.extensions import db
from flask_login import UserMixin
from app.models.base import BaseModel

class User(BaseModel, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(20), default="staff")

    def check_password(self, password, bcrypt):
        return bcrypt.check_password_hash(self.password_hash, password)