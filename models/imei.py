from app.extensions import db
from app.models.base import BaseModel

class IMEI(BaseModel):
    __tablename__ = "imeis"

    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    imei_code = db.Column(db.String(50), unique=True, nullable=False)

    status = db.Column(db.String(20), default="in_stock")

    purchase_items = db.relationship("PurchaseItem", backref="imei", lazy=True)
    sale_items = db.relationship("SaleItem", backref="imei", lazy=True)