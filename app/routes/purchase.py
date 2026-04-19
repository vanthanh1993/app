from flask import Blueprint, request, jsonify, render_template
from sqlalchemy.orm import joinedload

from app.models.imei import IMEI
from app.models.purchase import Purchase, PurchaseItem
from app.models.product import Product
from app.models.supplier import Supplier
from app.extensions import db

purchase_bp = Blueprint("purchase", __name__)


@purchase_bp.route("/purchase", methods=["GET", "POST"])
def purchase():

    if request.method == "GET":
        suppliers = Supplier.query.all()
        return render_template("purchase.html", suppliers=suppliers)

    try:
        data = request.get_json() or {}

        imeis = data.get("imeis", [])
        price = float(data.get("price", 0))
        supplier_id = data.get("supplier_id")
        product_name = (data.get("product_name") or "").strip()

        if not supplier_id:
            return jsonify({"message": "Chưa chọn nhà cung cấp"}), 400

        if not product_name:
            return jsonify({"message": "Chưa nhập tên sản phẩm"}), 400

        if not imeis:
            return jsonify({"message": "Chưa nhập IMEI"}), 400

        if price <= 0:
            return jsonify({"message": "Giá không hợp lệ"}), 400

        for code in imeis:
            if len(code) < 4 or len(code) > 15:
                return jsonify({"message": f"IMEI không hợp lệ: {code}"}), 400

        existing = IMEI.query.filter(IMEI.imei_code.in_(imeis)).all()
        if existing:
            return jsonify({
                "message": "IMEI đã tồn tại: " + ", ".join([i.imei_code for i in existing])
            }), 400

        product = Product.query.filter_by(name=product_name).first()
        if not product:
            product = Product(name=product_name)
            db.session.add(product)
            db.session.commit()

        purchase = Purchase(
            supplier_id=supplier_id,
            total_amount=price * len(imeis),
            paid_amount=0
        )
        db.session.add(purchase)
        db.session.commit()

        for code in imeis:
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

        return jsonify({"message": f"Nhập {len(imeis)} sản phẩm thành công!"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Lỗi hệ thống: {str(e)}"}), 500


@purchase_bp.route("/purchase/history")
def purchase_history():

    purchases = Purchase.query\
        .options(joinedload(Purchase.supplier))\
        .order_by(Purchase.id.desc())\
        .all()

    return render_template("purchase_history.html", purchases=purchases)


@purchase_bp.route("/purchase/<int:id>")
def purchase_detail(id):

    purchase = db.session.get(Purchase, id)

    if not purchase:
        return "Không tồn tại", 404

    items = db.session.query(PurchaseItem, IMEI)\
        .join(IMEI, PurchaseItem.imei_id == IMEI.id)\
        .filter(PurchaseItem.purchase_id == id).all()

    return render_template("purchase_detail.html",
                           purchase=purchase,
                           items=items)


# 🔥CHỨC NĂNG XOÁ
@purchase_bp.route("/purchase/remove-imei/<int:item_id>", methods=["POST"])
def remove_purchase_imei(item_id):

    item = db.session.get(PurchaseItem, item_id)

    if not item:
        return jsonify({"message": "Không tồn tại"}), 404

    imei = db.session.get(IMEI, item.imei_id)

    if imei.status == "sold":
        return jsonify({"message": "IMEI đã bán, không thể xoá"}), 400

    db.session.delete(imei)
    db.session.delete(item)
    db.session.commit()

    return jsonify({"message": "Đã xoá"})


# 🔥UPDATE GIÁ
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


# 🔥UPDATE TOTAL
@purchase_bp.route("/purchase/update-total/<int:id>")
def update_purchase_total(id):

    items = PurchaseItem.query.filter_by(purchase_id=id).all()

    total = sum([float(i.price) for i in items])

    purchase = db.session.get(Purchase, id)
    purchase.total_amount = total

    db.session.commit()

    return jsonify({"total": total})
 
# CHECK IMEI 
@purchase_bp.route("/purchase/check-imei", methods=["POST"])
def check_imei():

    data = request.get_json() or {}
    code = (data.get("imei") or "").strip()

    # ❌ rỗng
    if not code:
        return jsonify({
            "valid": False,
            "message": "IMEI rỗng"
        })

    # ❌ độ dài sai (tuỳ bạn chỉnh)
    if len(code) < 4 or len(code) > 20:
        return jsonify({
            "valid": False,
            "message": "IMEI không hợp lệ"
        })

    # ❌ trùng
    exists = IMEI.query.filter_by(imei_code=code).first()

    if exists:
        return jsonify({
            "valid": False,
            "message": "IMEI đã tồn tại"
        })

    # ✅ ok
    return jsonify({
        "valid": True
    })
    
# UPDATE IMEI   
@purchase_bp.route("/purchase/update-imei/<int:id>", methods=["POST"])
def update_imei(id):

    data = request.get_json() or {}
    new_code = (data.get("imei") or "").strip()

    # ❌ validate rỗng
    if not new_code:
        return jsonify({"message": "IMEI không được rỗng"}), 400

    # ❌ validate độ dài
    if len(new_code) < 4 or len(new_code) > 20:
        return jsonify({"message": "IMEI không hợp lệ"}), 400

    # 🔎 tìm item
    item = db.session.get(PurchaseItem, id)
    if not item:
        return jsonify({"message": "Không tìm thấy item"}), 404

    imei = db.session.get(IMEI, item.imei_id)
    if not imei:
        return jsonify({"message": "Không tìm thấy IMEI"}), 404

    # ❌ check trùng (trừ chính nó)
    exists = IMEI.query.filter(
        IMEI.imei_code == new_code,
        IMEI.id != imei.id
    ).first()

    if exists:
        return jsonify({"message": "IMEI đã tồn tại"}), 400

    # ✅ update
    imei.imei_code = new_code
    db.session.commit()

    return jsonify({
        "message": "Cập nhật thành công"
    })    