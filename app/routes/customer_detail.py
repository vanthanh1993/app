from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import func

from app.extensions import db
from app.models.customer import Customer
from app.models.sale import Sale
from app.models.customer_payment import CustomerPayment

customer_detail_bp = Blueprint("customer_detail", __name__)


@customer_detail_bp.route("/customer/<int:id>")
def customer_detail(id):
    customer = db.session.get(Customer, id)

    if not customer:
        return "Không tìm thấy khách hàng", 404

    total_sale = db.session.query(func.sum(Sale.total_amount))\
        .filter(Sale.customer_id == id).scalar() or 0

    total_paid = db.session.query(func.sum(CustomerPayment.amount))\
        .filter(CustomerPayment.customer_id == id).scalar() or 0

    debt = total_sale - total_paid

    sales = Sale.query.filter_by(customer_id=id).all()
    payments = CustomerPayment.query.filter_by(customer_id=id).all()

    return render_template(
        "customer_detail.html",
        customer=customer,
        total_sale=total_sale,
        total_paid=total_paid,
        debt=debt,
        sales=sales,
        payments=payments
    )


@customer_detail_bp.route("/customer/pay/<int:id>", methods=["POST"])
def pay_customer(id):
    data = request.get_json() or {}

    try:
        amount = float(data.get("amount", 0))
    except:
        return jsonify({"message": "Số tiền không hợp lệ"}), 400

    if amount <= 0:
        return jsonify({"message": "Số tiền không hợp lệ"}), 400

    customer = db.session.get(Customer, id)
    if not customer:
        return jsonify({"message": "Không tồn tại khách hàng"}), 404

    payment = CustomerPayment(
        customer_id=id,
        amount=amount,
        note=data.get("note", "")
    )

    db.session.add(payment)
    db.session.commit()

    return jsonify({"message": "Thanh toán thành công!"})