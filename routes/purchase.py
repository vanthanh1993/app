from flask import Blueprint, request, jsonify, render_template
from sqlalchemy.orm import joinedload

from app.models.imei import IMEI
from app.models.purchase import Purchase, PurchaseItem
from app.models.product import Product
from app.models.supplier import Supplier
from app.extensions import db

purchase_bp = Blueprint("purchase", __name__)


# =========================
# 🔧 HELPERS
# =========================

def validate_imei(code):
    code = (code or "").strip()

    if not code:
        return False, "IMEI rỗng"

    if len(code) < 4 or len(code) > 20:
        return False, f"IMEI không hợp lệ: {code}"

    return True, code


def get_existing_imeis(imeis):
    if not imeis:
        return []

    existing = IMEI.query.filter(IMEI.imei_code.in_(imeis)).all()
    return [i.imei_code for i in existing]


def imei_exists(code, exclude_id=None):
    q = IMEI.query.filter(IMEI.imei_code == code)

    if exclude_id:
        q = q.filter(IMEI.id != exclude_id)

    return q.first() is not None


# =========================
# 📥 PURCHASE
# =========================

@purchase_bp.route("/purchase", methods=["GET", "POST"])
def purchase():

    # ===== GET =====
    if request.method == "GET":
        suppliers = Supplier.query.all()
        return render_template("purchase.html", suppliers=suppliers)

    # ===== POST =====
    try:
        data = request.get_json() or {}

        imeis = data.get("imeis", [])
        price = float(data.get("price", 0))
        supplier_id = data.get("supplier_id")
        product_name = (data.get("product_name") or "").strip()

        # ===== VALIDATE =====
        if not supplier_id:
            return jsonify({"message": "Chưa chọn nhà cung cấp"}), 400

        if not product_name:
            return jsonify({"message": "Chưa nhập tên sản phẩm"}), 400

        if not imeis:
            return jsonify({"message": "Chưa nhập IMEI"}), 400

        if price <= 0:
            return jsonify({"message": "Giá không hợp lệ"}), 400

        # validate IMEI từng cái
        clean_imeis = []
        for code in imeis:
            ok, result = validate_imei(code)
            if not ok:
                return jsonify({"message": result}), 400
            clean_imeis.append(result)

        # check trùng DB
        existing = get_existing_imeis(clean_imeis)
        if existing:
            return jsonify({
                "message": "IMEI đã tồn tại: " + ", ".join(existing)
            }), 400

        # ===== PRODUCT =====
        product = Product.query.filter_by(name=product_name).first()

        if not product:
            product = Product(name=product_name)
            db.session.add(product)
            db.session.flush()

        # ===== PURCHASE =====
        purchase = Purchase(
            supplier_id=supplier_id,
            total_amount=price * len(clean_imeis),
            paid_amount=0
        )
        db.session.add(purchase)
        db.session.flush()

        # ===== ITEMS =====
        for code in clean_imeis:
            imei = IMEI(
                imei_code=code,
                product_id=product.id,
                status="in_stock"
            )
            db.session.add(imei)
            db.session.flush()

            item = PurchaseItem(
                purchase_id=purchase.id,
                imei_id=imei.id,
                price=price
            )
            db.session.add(item)

        db.session.commit()

        return jsonify({
            "message": f"Nhập {len(clean_imeis)} sản phẩm thành công!"
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Lỗi hệ thống: {str(e)}"}), 500


# =========================
# 📜 HISTORY
# =========================

@purchase_bp.route("/purchase/history")
def purchase_history():

    purchases = Purchase.query\
        .options(joinedload(Purchase.supplier))\
        .order_by(Purchase.id.desc())\
        .all()

    return render_template("purchase_history.html", purchases=purchases)


# =========================
# 🔍 DETAIL
# =========================

@purchase_bp.route("/purchase/<int:id>")
def purchase_detail(id):

    purchase = db.session.get(Purchase, id)

    if not purchase:
        return "Không tồn tại", 404

    items = db.session.query(PurchaseItem, IMEI)\
        .join(IMEI, PurchaseItem.imei_id == IMEI.id)\
        .filter(PurchaseItem.purchase_id == id).all()

    return render_template(
        "purchase_detail.html",
        purchase=purchase,
        items=items
    )


# =========================
# ❌ REMOVE IMEI
# =========================

@purchase_bp.route("/purchase/remove-imei/<int:item_id>", methods=["POST"])
def remove_purchase_imei(item_id):

    item = db.session.get(PurchaseItem, item_id)

    if not item:
        return jsonify({"message": "Không tồn tại"}), 404

    imei = db.session.get(IMEI, item.imei_id)

    if imei.status == "sold":
        return jsonify({"message": "IMEI đã bán"}), 400

    db.session.delete(imei)
    db.session.delete(item)
    db.session.commit()

    return jsonify({"message": "Đã xoá"})


# =========================
# 💰 UPDATE PRICE
# =========================

@purchase_bp.route("/purchase/update-price/<int:item_id>", methods=["POST"])
def update_purchase_price(item_id):

    data = request.get_json() or {}

    try:
        price = float(data.get("price", 0))
    except:
        return jsonify({"message": "Giá không hợp lệ"}), 400

    item = db.session.get(PurchaseItem, item_id)

    if not item:
        return jsonify({"message": "Không tồn tại"}), 404

    item.price = price
    db.session.commit()

    return jsonify({"message": "OK"})


# =========================
# 🔄 UPDATE TOTAL
# =========================

@purchase_bp.route("/purchase/update-total/<int:id>")
def update_purchase_total(id):

    items = PurchaseItem.query.filter_by(purchase_id=id).all()

    total = sum([float(i.price) for i in items])

    purchase = db.session.get(Purchase, id)
    purchase.total_amount = total

    db.session.commit()

    return jsonify({"total": total})


# =========================
# 🔍 CHECK 1 IMEI
# =========================

@purchase_bp.route("/purchase/check-imei", methods=["POST"])
def check_imei():

    data = request.get_json() or {}
    code = data.get("imei")

    ok, result = validate_imei(code)
    if not ok:
        return jsonify({"valid": False, "message": result})

    if imei_exists(result):
        return jsonify({"valid": False, "message": "IMEI đã tồn tại"})

    return jsonify({"valid": True})


# =========================
# 🚀 CHECK BULK IMEI
# =========================

@purchase_bp.route("/purchase/check-imei-bulk", methods=["POST"])
def check_imei_bulk():

    data = request.get_json() or {}
    imeis = data.get("imeis", [])

    existing = get_existing_imeis(imeis)

    return jsonify({
        "exists": existing
    })


# =========================
# ✏️ UPDATE IMEI
# =========================

@purchase_bp.route("/purchase/update-imei/<int:id>", methods=["POST"])
def update_imei(id):

    data = request.get_json() or {}
    new_code = data.get("imei")

    ok, result = validate_imei(new_code)
    if not ok:
        return jsonify({"message": result}), 400

    item = db.session.get(PurchaseItem, id)
    if not item:
        return jsonify({"message": "Không tìm thấy item"}), 404

    imei = db.session.get(IMEI, item.imei_id)
    if not imei:
        return jsonify({"message": "Không tìm thấy IMEI"}), 404

    if imei_exists(result, exclude_id=imei.id):
        return jsonify({"message": "IMEI đã tồn tại"}), 400

    imei.imei_code = result
    db.session.commit()

    return jsonify({"message": "Cập nhật thành công"})