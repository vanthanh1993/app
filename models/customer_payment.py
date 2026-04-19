from app.extensions import db
from app.models.base import BaseModel

class CustomerPayment(BaseModel):
    __tablename__ = "customer_payments"

    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id"),
        nullable=False
    )

    amount = db.Column(db.Numeric, nullable=False)
    note = db.Column(db.String(255))