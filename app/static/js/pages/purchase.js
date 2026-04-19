document.addEventListener("DOMContentLoaded", () => {

    const priceInput = document.getElementById("price");
    const imeiInput = document.getElementById("imeis");
    const qtyEl = document.getElementById("qty");
    const totalEl = document.getElementById("total");
    const warningEl = document.getElementById("imeiWarning");
    const form = document.getElementById("purchaseForm");

    let duplicateList = [];
    let dbDuplicate = [];
    let debounceTimer;

    function formatVN(num){
        return new Intl.NumberFormat('vi-VN').format(num || 0);
    }

    function parseNumber(str){
        return parseInt(str.replace(/\D/g,'')) || 0;
    }

    function updateTotal(){
        let price = parseNumber(priceInput.value);
        let qty = parseInt(qtyEl.innerText) || 0;
        totalEl.innerText = formatVN(price * qty);
    }

    // ===== FORMAT PRICE =====
    priceInput.addEventListener("input", function(){
        let raw = this.value.replace(/\D/g,'');
        this.value = formatVN(raw);
        updateTotal();
    });

    // ===== CHECK DB =====
    async function checkIMEIFromDB(imeis){
        try{
            const res = await fetch("/purchase/check-imei-bulk", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ imeis })
            });
            const data = await res.json();
            return data.exists || [];
        }catch{
            return [];
        }
    }

    function renderWarning(){
        let msg = "";

        if(duplicateList.length > 0){
            msg += "⚠️ Trùng nội bộ : " + duplicateList.join(", ") + "\n";
        }

        if(dbDuplicate.length > 0){
            msg += "❌ Đã tồn tại DB : " + dbDuplicate.join(", ");
        }

        warningEl.innerText = msg;
    }

    // ===== IMEI INPUT =====
    imeiInput.addEventListener("input", () => {

        let lines = imeiInput.value
            .split("\n")
            .map(x => x.trim())
            .filter(x => x);

        // local duplicate
        let seen = new Set();
        duplicateList = [];

        lines.forEach(x => {
            if(seen.has(x)) duplicateList.push(x);
            else seen.add(x);
        });

        qtyEl.innerText = lines.length;
        updateTotal();

        // debounce DB check
        clearTimeout(debounceTimer);

        debounceTimer = setTimeout(async () => {
            dbDuplicate = await checkIMEIFromDB(lines);
            renderWarning();
        }, 400);
    });

    // ===== SUBMIT =====
    form.addEventListener("submit", async function(e){
        e.preventDefault();

        let imeis = imeiInput.value
            .split("\n")
            .map(x => x.trim())
            .filter(x => x);

        let price = parseNumber(priceInput.value);

        if(duplicateList.length > 0){
            alert("IMEI trùng trong danh sách");
            return;
        }

        if(dbDuplicate.length > 0){
            alert("IMEI đã tồn tại trong hệ thống");
            return;
        }

        if(!this.supplier_id.value || !this.product_name.value){
            alert("Thiếu thông tin");
            return;
        }

        if(imeis.length === 0){
            alert("Chưa nhập IMEI");
            return;
        }

        if(price <= 0){
            alert("Giá không hợp lệ");
            return;
        }

        try{
            const res = await fetch("/purchase", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    imeis,
                    price,
                    supplier_id: this.supplier_id.value,
                    product_name: this.product_name.value
                })
            });

            const data = await res.json();

            alert(data.message);

            form.reset();
            qtyEl.innerText = 0;
            totalEl.innerText = 0;
            warningEl.innerText = "";

        }catch{
            alert("Lỗi hệ thống");
        }
    });

});
