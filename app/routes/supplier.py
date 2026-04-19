from flask import Blueprint, render_template, request, redirect, jsonify, url_for
from sqlalchemy import func

from app.extensions import db
from app.models.supplier import Supplier
from app.models.purchase import Purchase
from app.models.payment import SupplierPayment

supplier_bp = Blueprint("supplier", __name__)


# 📋 LIST
@supplier_bp.route("/suppliers")
def suppliers():
    data = Supplier.query.all()

    for s in data:
        has_purchase = Purchase.query.filter_by(supplier_id=s.id).first()
        has_payment = SupplierPayment.query.filter_by(supplier_id=s.id).first()
        s.has_transaction = bool(has_purchase or has_payment)

    return render_template("suppliers.html", suppliers=data)


# ➕ ADD
@supplier_bp.route("/supplier/add", methods=["POST"])
def add_supplier():
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    address = request.form.get("address", "").strip()

    if not name or not phone or not address:
        return "Không được để trống!", 400

    if not phone.isdigit():
        return "SĐT không hợp lệ!", 400

    s = Supplier(name=name, phone=phone, address=address)

    db.session.add(s)
    db.session.commit()

    return redirect(url_for("supplier.suppliers"))


# ✏️ EDIT
@supplier_bp.route("/supplier/edit/<int:id>", methods=["POST"])
def edit_supplier(id):
    s = db.session.get(Supplier, id)

    if not s:
        return "Không tồn tại NCC", 404

    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    address = request.form.get("address", "").strip()

    if not name or not phone or not address:
        return "Không được để trống!", 400

    if not phone.isdigit():
        return "SĐT không hợp lệ!", 400

    s.name = name
    s.phone = phone
    s.address = address

    db.session.commit()

    return redirect(url_for("supplier.supplier_detail", id=id))


# ❌ DELETE → ✅ POST
@supplier_bp.route("/supplier/delete/<int:id>", methods=["POST"])
def delete_supplier(id):
    s = db.session.get(Supplier, id)

    if not s:
        return redirect(url_for("supplier.suppliers"))

    has_purchase = Purchase.query.filter_by(supplier_id=id).first()
    has_payment = SupplierPayment.query.filter_by(supplier_id=id).first()

    if has_purchase or has_payment:
        return "Không thể xoá NCC đã có giao dịch!", 400

    db.session.delete(s)
    db.session.commit()

    return redirect(url_for("supplier.suppliers"))


# 📊 DETAIL
@supplier_bp.route("/supplier/<int:id>")
def supplier_detail(id):
    supplier = db.session.get(Supplier, id)

    if not supplier:
        return "Không tồn tại NCC", 404

    purchases = Purchase.query.filter_by(supplier_id=id).all()

    total_import = db.session.query(func.sum(Purchase.total_amount))\
        .filter(Purchase.supplier_id == id).scalar() or 0

    total_paid = db.session.query(func.sum(SupplierPayment.amount))\
        .filter(SupplierPayment.supplier_id == id).scalar() or 0

    debt = total_import - total_paid

    payments = SupplierPayment.query\
        .filter_by(supplier_id=id)\
        .order_by(SupplierPayment.created_at.desc())\
        .all()

    return render_template(
        "supplier_detail.html",
        supplier=supplier,
        purchases=purchases,
        total_import=total_import,
        total_paid=total_paid,
        debt=debt,
        payments=payments
    )


# 💰 PAYMENT
@supplier_bp.route("/supplier/pay/<int:id>", methods=["POST"])
def pay_supplier(id):
    data = request.get_json() or {}

    try:
        amount = float(data.get("amount", 0))
    except:
        return jsonify({"message": "Số tiền không hợp lệ"}), 400

    if amount <= 0:
        return jsonify({"message": "Số tiền không hợp lệ"}), 400

    supplier = db.session.get(Supplier, id)
    if not supplier:
        return jsonify({"message": "NCC không tồn tại"}), 404

    payment = SupplierPayment(
        supplier_id=id,
        amount=amount,
        note=data.get("note", "")
    )

    db.session.add(payment)
    db.session.commit()

    return jsonify({"message": "Thanh toán thành công!"})