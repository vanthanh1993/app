from app.extensions import db
from app.models.base import BaseModel

class Customer(BaseModel):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(255), nullable=False)

    sales = db.relationship("Sale", backref="customer", lazy=True)
    payments = db.relationship("CustomerPayment", backref="customer", lazy=True)