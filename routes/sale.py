from flask import Blueprint, render_template, request, jsonify
from sqlalchemy.orm import joinedload

from app.models.customer import Customer
from app.models.imei import IMEI
from app.models.sale import Sale, SaleItem
from app.extensions import db

sale_bp = Blueprint("sale", __name__)


# =========================
# 🔧 HELPERS
# =========================

def detect_duplicates(imeis):
    seen = set()
    duplicates = set()

    for code in imeis:
        if code in seen:
            duplicates.add(code)
        seen.add(code)

    return duplicates


def get_imeis_map(imeis):
    """Query 1 lần, trả về dict {imei_code: IMEI}"""
    records = IMEI.query.filter(IMEI.imei_code.in_(imeis)).all()
    return {i.imei_code: i for i in records}


def is_sellable(imei):
    return imei.status == "in_stock"


def calc_total(items):
    return sum(float(i.get("price", 0)) for i in items)


# =========================
# 📄 PAGE
# =========================

@sale_bp.route("/sale", methods=["GET"])
def sale_page():
    customers = Customer.query.all()
    return render_template("sale.html", customers=customers)


# =========================
# 🔍 CHECK IMEI (BULK)
# =========================

@sale_bp.route("/sale/check-imei", methods=["POST"])
def check_imei():

    data = request.get_json() or {}
    imeis = data.get("imeis", [])

    result = []

    duplicates = detect_duplicates(imeis)
    imei_map = get_imeis_map(imeis)

    for code in imeis:

        # duplicate trong input
        if code in duplicates:
            result.append({
                "imei": code,
                "status": "duplicate",
                "error": "Trùng IMEI"
            })
            continue

        imei = imei_map.get(code)

        # không tồn tại
        if not imei:
            result.append({
                "imei": code,
                "status": "not_found",
                "error": "Không tồn tại"
            })
            continue

        # đã bán
        if not is_sellable(imei):
            result.append({
                "imei": code,
                "status": "sold",
                "error": "Đã bán"
            })
            continue

        # OK
        result.append({
            "imei": code,
            "product": imei.product.name,
            "imei_id": imei.id,
            "status": "ok"
        })

    return jsonify(result)


# =========================
# 💾 CREATE SALE
# =========================

@sale_bp.route("/sale", methods=["POST"])
def create_sale():

    data = request.get_json() or {}

    customer_id = data.get("customer_id")
    items = data.get("items", [])

    if not items:
        return jsonify({"message": "Chưa có sản phẩm"}), 400

    # total
    total = calc_total(items)

    try:
        sale = Sale(
            customer_id=customer_id,
            total_amount=total,
            paid_amount=0
        )
        db.session.add(sale)
        db.session.flush()  # ⚠️ không commit

        imei_ids = [i["imei_id"] for i in items]
        imeis = IMEI.query.filter(IMEI.id.in_(imei_ids)).all()
        imei_map = {i.id: i for i in imeis}

        for i in items:

            imei = imei_map.get(i["imei_id"])

            if not imei:
                raise Exception("IMEI không tồn tại")

            # chống race condition
            if not is_sellable(imei):
                raise Exception(f"IMEI {imei.imei_code} đã bán")

            item = SaleItem(
                sale_id=sale.id,
                imei_id=imei.id,
                price=float(i["price"])
            )
            db.session.add(item)

            # update trạng thái
            imei.status = "sold"

        db.session.commit()

        return jsonify({"message": "Bán hàng thành công!"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 400


# =========================
# 📜 DETAIL
# =========================

@sale_bp.route("/sale/<int:id>")
def sale_detail(id):

    sale = db.session.get(Sale, id)

    if not sale:
        return "Đơn không tồn tại", 404

    items = db.session.query(SaleItem, IMEI)\
        .join(IMEI, SaleItem.imei_id == IMEI.id)\
        .filter(SaleItem.sale_id == id)\
        .all()

    return render_template(
        "sale_detail.html",
        sale=sale,
        items=items
    )


# =========================
# ❌ REMOVE IMEI
# =========================

@sale_bp.route("/sale/remove-imei/<int:item_id>", methods=["POST"])
def remove_imei(item_id):

    item = db.session.get(SaleItem, item_id)

    if not item:
        return jsonify({"message": "Không tồn tại"}), 404

    imei = db.session.get(IMEI, item.imei_id)

    # trả lại kho
    imei.status = "in_stock"

    db.session.delete(item)
    db.session.commit()

    return jsonify({"message": "Đã xoá"})


# =========================
# 💰 UPDATE PRICE
# =========================

@sale_bp.route("/sale/update-price/<int:item_id>", methods=["POST"])
def update_price(item_id):

    data = request.get_json() or {}

    try:
        price = float(data.get("price", 0))
    except:
        return jsonify({"message": "Giá không hợp lệ"}), 400

    item = db.session.get(SaleItem, item_id)

    if not item:
        return jsonify({"message": "Không tồn tại"}), 404

    item.price = price
    db.session.commit()

    return jsonify({"message": "OK"})


# =========================
# 🔄 UPDATE TOTAL
# =========================

@sale_bp.route("/sale/update-total/<int:sale_id>")
def update_total(sale_id):

    items = SaleItem.query.filter_by(sale_id=sale_id).all()
    total = sum(i.price for i in items)

    sale = db.session.get(Sale, sale_id)
    sale.total_amount = total

    db.session.commit()

    return jsonify({"total": total})