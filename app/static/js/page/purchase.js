const priceInput = document.getElementById("price");
const imeiInput = document.getElementById("imeis");

const qtyEl = document.getElementById("qty");
const totalEl = document.getElementById("total");


// ===== FORMAT PRICE =====
bindMoneyInput(priceInput, updateTotal);


// ===== COUNT IMEI =====
imeiInput.addEventListener("input", () => {

    let lines = imeiInput.value
        .split("\n")
        .map(x => x.trim())
        .filter(x => x);

    qtyEl.innerText = lines.length;

    updateTotal();
});


// ===== UPDATE TOTAL =====
function updateTotal(){

    let price = parseNumber(priceInput.value);
    let qty = parseInt(qtyEl.innerText) || 0;

    totalEl.innerText = formatVN(price * qty);
}


// ===== SUBMIT =====
document.getElementById("purchaseForm")?.addEventListener("submit", async function(e){

    e.preventDefault();

    let imeis = imeiInput.value
        .split("\n")
        .map(x => x.trim())
        .filter(x => x);

    if(imeis.length === 0){
        alert("⚠️ Chưa nhập IMEI");
        return;
    }

    try{

        const res = await api("{{ url_for('purchase.purchase_page') }}", "POST", {
            imeis,
            price: parseNumber(priceInput.value),
            supplier_id: this.supplier_id.value,
            product_name: this.product_name.value
        });

        alert(res.message);

        // RESET
        this.reset();
        qtyEl.innerText = 0;
        totalEl.innerText = 0;

    }catch(e){
        alert("❌ " + e.message);
    }

});