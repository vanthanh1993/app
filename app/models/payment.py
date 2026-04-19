from app.extensions import db
from app.models.base import BaseModel

class SupplierPayment(BaseModel):
    __tablename__ = "supplier_payments"

    id = db.Column(db.Integer, primary_key=True)

    supplier_id = db.Column(
        db.Integer,
        db.ForeignKey("suppliers.id"),
        nullable=False
    )

    amount = db.Column(db.Numeric, nullable=False)
    note = db.Column(db.String(255))