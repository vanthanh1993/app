from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func

from app.extensions import db
from app.models.imei import IMEI
from app.models.sale import Sale
from app.models.purchase import Purchase
from app.models.customer_payment import CustomerPayment
from app.models.payment import SupplierPayment

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))
    return redirect(url_for("auth.login"))

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    total_stock = db.session.query(func.count(IMEI.id)).filter(IMEI.status == "in_stock").scalar() or 0
    total_sold = db.session.query(func.count(IMEI.id)).filter(IMEI.status == "sold").scalar() or 0

    revenue = db.session.query(func.sum(Sale.total_amount)).scalar() or 0
    import_cost = db.session.query(func.sum(Purchase.total_amount)).scalar() or 0

    customer_paid = db.session.query(func.sum(CustomerPayment.amount)).scalar() or 0
    supplier_paid = db.session.query(func.sum(SupplierPayment.amount)).scalar() or 0

    customer_debt = revenue - customer_paid
    supplier_debt = import_cost - supplier_paid
    profit = revenue - import_cost

    recent_sales = Sale.query.order_by(Sale.id.desc()).limit(5).all()

    return render_template(
        "dashboard.html",
        total_stock=total_stock,
        total_sold=total_sold,
        revenue=revenue,
        import_cost=import_cost,
        customer_debt=customer_debt,
        supplier_debt=supplier_debt,
        profit=profit,
        recent_sales=recent_sales
    )