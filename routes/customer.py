from flask import Blueprint, render_template, request, redirect, jsonify, url_for
from sqlalchemy import func, exists

from app.extensions import db
from app.models.customer import Customer
from app.models.sale import Sale
from app.models.customer_payment import CustomerPayment

customer_bp = Blueprint("customer", __name__)


def get_customers_with_flag(query):
    results = db.session.query(
        Customer,
        exists().where(Sale.customer_id == Customer.id),
        exists().where(CustomerPayment.customer_id == Customer.id)
    ).filter(Customer.id.in_([c.id for c in query])).all()

    customers = []
    for c, has_sale, has_payment in results:
        c.has_transaction = bool(has_sale or has_payment)
        customers.append(c)

    return customers


@customer_bp.route("/customers")
def customers():
    base_query = Customer.query.order_by(Customer.id.desc()).all()
    data = get_customers_with_flag(base_query)
    return render_template("customers.html", customers=data)


@customer_bp.route("/customer/add", methods=["POST"])
def add_customer():
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    address = request.form.get("address", "").strip()

    if not name or not phone or not address:
        return "Không được để trống thông tin!", 400

    if not phone.isdigit():
        return "SĐT không hợp lệ!", 400

    c = Customer(name=name, phone=phone, address=address)
    db.session.add(c)
    db.session.commit()

    return redirect(url_for("customer.customers"))


@customer_bp.route("/customer/<int:id>")
def detail(id):
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
        debt=debt,
        sales=sales,
        payments=payments
    )


@customer_bp.route("/customer/edit/<int:id>", methods=["POST"])
def edit_customer(id):
    c = db.session.get(Customer, id)

    if not c:
        return "Không tồn tại", 404

    c.name = request.form.get("name", "").strip()
    c.phone = request.form.get("phone", "").strip()
    c.address = request.form.get("address", "").strip()

    db.session.commit()

    return redirect(url_for("customer.detail", id=id))


@customer_bp.route("/customer/delete/<int:id>", methods=["POST"])
def delete_customer(id):
    customer = db.session.get(Customer, id)

    if not customer:
        return jsonify({"success": False, "message": "Không tồn tại"}), 404

    has_sale = db.session.query(exists().where(Sale.customer_id == id)).scalar()
    has_payment = db.session.query(exists().where(CustomerPayment.customer_id == id)).scalar()

    if has_sale or has_payment:
        return jsonify({"success": False, "message": "Khách hàng đã có giao dịch"}), 400

    db.session.delete(customer)
    db.session.commit()

    return jsonify({"success": True})


# ===================== SEARCH =====================
@customer_bp.route("/customer/search")
def search_customer():

    name = request.args.get("name", "").strip()
    phone = request.args.get("phone", "").strip()
    address = request.args.get("address", "").strip()

    query = Customer.query

    if name:
        query = query.filter(Customer.name.ilike(f"%{name}%"))

    if phone:
        query = query.filter(Customer.phone.ilike(f"%{phone}%"))

    if address:
        query = query.filter(Customer.address.ilike(f"%{address}%"))

    base_query = query.order_by(Customer.id.desc()).all()

    customers = get_customers_with_flag(base_query)

    return render_template("customers.html", customers=customers)    