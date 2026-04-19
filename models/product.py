from app.extensions import db
from app.models.base import BaseModel

class Product(BaseModel):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    brand = db.Column(db.String(100))

    imeis = db.relationship("IMEI", backref="product", lazy=True)