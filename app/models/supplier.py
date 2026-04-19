from app.extensions import db
from app.models.base import BaseModel

class Supplier(BaseModel):
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50))
    address = db.Column(db.Text)

    purchases = db.relationship("Purchase", backref="supplier", lazy=True)
    payments = db.relationship("SupplierPayment", backref="supplier", lazy=True)