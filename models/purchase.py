from app.extensions import db
from app.models.base import BaseModel

class Purchase(BaseModel):
    __tablename__ = "purchases"

    id = db.Column(db.Integer, primary_key=True)

    supplier_id = db.Column(
        db.Integer,
        db.ForeignKey("suppliers.id"),
        nullable=False
    )

    total_amount = db.Column(db.Numeric, default=0)
    paid_amount = db.Column(db.Numeric, default=0)

    items = db.relationship("PurchaseItem", backref="purchase", lazy=True)

    @property
    def product_names(self):
        return list({
            item.imei.product.name
            for item in self.items
            if item.imei and item.imei.product
        })


class PurchaseItem(db.Model):
    __tablename__ = "purchase_items"

    id = db.Column(db.Integer, primary_key=True)

    purchase_id = db.Column(
        db.Integer,
        db.ForeignKey("purchases.id"),
        nullable=False
    )

    imei_id = db.Column(
        db.Integer,
        db.ForeignKey("imeis.id"),
        nullable=False
    )

    price = db.Column(db.Numeric, nullable=False)

    @property
    def product_name(self):
        if self.imei and self.imei.product:
            return self.imei.product.name
        return "N/A"