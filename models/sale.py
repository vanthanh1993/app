from collections import Counter
from app.extensions import db
from app.models.base import BaseModel

class Sale(BaseModel):
    __tablename__ = "sales"

    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id"),
        nullable=False
    )

    total_amount = db.Column(db.Numeric, default=0)
    paid_amount = db.Column(db.Numeric, default=0)

    items = db.relationship("SaleItem", backref="sale", lazy=True)

    @property
    def product_qty(self):
        names = [
            item.imei.product.name
            for item in self.items
            if item.imei and item.imei.product
        ]
        return Counter(names)


class SaleItem(db.Model):
    __tablename__ = "sale_items"

    id = db.Column(db.Integer, primary_key=True)

    sale_id = db.Column(
        db.Integer,
        db.ForeignKey("sales.id"),
        nullable=False
    )

    imei_id = db.Column(
        db.Integer,
        db.ForeignKey("imeis.id"),
        nullable=False
    )

    price = db.Column(db.Numeric, nullable=False)