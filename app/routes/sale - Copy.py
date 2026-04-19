from flask import Blueprint, render_template, request, jsonify
from app.models.customer import Customer
from app.models.imei import IMEI
from app.models.sale import Sale, SaleItem
from app.extensions import db

sale_bp = Blueprint("sale", __name__)


@sale_bp.route("/sale", methods=["GET"])
def sale_page():
    customers = Customer.query.all()
    return render_template("sale.html", customers=customers)


# ✅ FIX CHÍNH Ở ĐÂY
@sale_bp.route("/sale/check-imei", methods=["POST"])
def check_imei():

    data = request.get_json()
    imeis = data.get("imeis", [])

    result = []
    seen = set()  # chống trùng IMEI

    for code in imeis:

        # 🔥 chống nhập trùng
        if code in seen:
            result.append({
                "imei": code,
                "status": "duplicate",
                "error": "Trùng IMEI"
            })
            continue
        seen.add(code)

        imei = IMEI.query.filter_by(imei_code=code).first()

        # ❌ không tồn tại
        if not imei:
            result.append({
                "imei": code,
                "status": "not_found",
                "error": "Không tồn tại"
            })
            continue

        # ❌ đã bán / không còn trong kho
        if imei.status != "in_stock":
            result.append({
                "imei": code,
                "status": "sold",
                "error": "Đã bán"
            })
            continue

        # ✅ hợp lệ
        result.append({
            "imei": code,
            "product": imei.product.name,
            "imei_id": imei.id,
            "status": "ok"
        })

    return jsonify(result)


@sale_bp.route("/sale", methods=["POST"])
def create_sale():

    data = request.get_json()

    customer_id = data["customer_id"]
    items = data["items"]  # [{imei_id, price}]

    if not items:
        return jsonify({"message": "Chưa có sản phẩm"}), 400

    # 🔥 đảm bảo price là số
    total = sum([float(i["price"]) for i in items])

    sale = Sale(
        customer_id=customer_id,
        total_amount=total,
        paid_amount=0
    )

    db.session.add(sale)
    db.session.commit()

    for i in items:

        imei = IMEI.query.get(i["imei_id"])

        # 🔥 CHỐNG BÁN TRÙNG (race condition)
        if imei.status != "in_stock":
            return jsonify({
                "message": f"IMEI {imei.imei_code} đã bán trước đó"
            }), 400

        item = SaleItem(
            sale_id=sale.id,
            imei_id=i["imei_id"],
            price=float(i["price"])
        )
        db.session.add(item)

        # update trạng thái IMEI
        imei.status = "sold"

    db.session.commit()

    return jsonify({"message": "Bán hàng thành công!"})


@sale_bp.route("/sale/<int:id>")
def sale_detail(id):

    sale = Sale.query.get(id)

    if not sale:
        return "Đơn không tồn tại", 404

    items = db.session.query(SaleItem, IMEI)\
        .join(IMEI, SaleItem.imei_id == IMEI.id)\
        .filter(SaleItem.sale_id == id).all()

    return render_template("sale_detail.html",
                           sale=sale,
                           items=items)


@sale_bp.route("/sale/remove-imei/<int:item_id>", methods=["POST"])
def remove_imei(item_id):

    item = SaleItem.query.get(item_id)

    if not item:
        return jsonify({"message": "Không tồn tại"}), 404

    # trả lại kho
    imei = IMEI.query.get(item.imei_id)
    imei.status = "in_stock"

    db.session.delete(item)
    db.session.commit()

    return jsonify({"message": "Đã xoá"})


@sale_bp.route("/sale/update-price/<int:item_id>", methods=["POST"])
def update_price(item_id):

    data = request.get_json()
    price = float(data.get("price", 0))

    item = SaleItem.query.get(item_id)

    if not item:
        return jsonify({"message": "Không tồn tại"}), 404

    item.price = price
    db.session.commit()

    return jsonify({"message": "OK"})


@sale_bp.route("/sale/update-total/<int:sale_id>")
def update_total(sale_id):

    items = SaleItem.query.filter_by(sale_id=sale_id).all()
    total = sum([i.price for i in items])

    sale = Sale.query.get(sale_id)
    sale.total_amount = total

    db.session.commit()

    return jsonify({"total": total})