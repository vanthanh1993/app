const textarea = document.getElementById("imei_input");
const listDiv = document.getElementById("list");
const totalEl = document.getElementById("total");
const emptyEl = document.getElementById("empty");

let groupedData = {};
let errorIMEI = [];

// ===== INPUT IMEI =====
textarea.addEventListener("input", debounce(async () => {

    let imeis = textarea.value
        .split("\n")
        .map(x => x.trim())
        .filter(x => x);

    if(!imeis.length){
        groupedData = {};
        errorIMEI = [];
        render();
        return;
    }

    try{

        const data = await api(API_CHECK, "POST", { imeis });

        groupedData = {};
        errorIMEI = [];

        data.forEach(i => {

            if(i.status !== "ok"){
                errorIMEI.push(i);
                return;
            }

            if(!groupedData[i.product]){
                groupedData[i.product] = [];
            }

            groupedData[i.product].push(i);
        });

        render();

    }catch(e){
        console.error(e);
    }

}, 300));


// ===== RENDER =====
function render(){

    listDiv.innerHTML = "";
    renderStatus();

    if(!Object.keys(groupedData).length){
        emptyEl.style.display = "block";
        totalEl.innerText = "0 đ";
        return;
    }

    emptyEl.style.display = "none";

    for(let product in groupedData){

        let group = groupedData[product];

        listDiv.innerHTML += `
        <div class="card card-product shadow-sm">

            <div class="card-body p-2">

                <div class="d-flex justify-content-between align-items-center">

                    <div>
                        <b>${product}</b>
                        <div class="small text-muted">${group.length} IMEI</div>
                    </div>

                    <input class="form-control text-end price-input"
                        placeholder="Giá"
                        data-product="${product}">
                </div>

                <div class="mt-2">
                    ${group.map(i => `
                        <span class="badge badge-imei me-1 mb-1">${i.imei}</span>
                    `).join("")}
                </div>

            </div>

        </div>
        `;
    }

    bindPrice();
}


// ===== STATUS =====
function renderStatus(){

    const box = document.getElementById("imeiStatus");

    if(errorIMEI.length === 0){
        box.innerHTML = "";
        return;
    }

    box.innerHTML = errorIMEI.map(i => {

        let text = "Không tồn tại";
        let cls = "status-notfound";

        if(i.status === "sold"){
            text = "Đã bán";
            cls = "status-sold";
        }
        else if(i.status === "duplicate"){
            text = "Trùng";
            cls = "status-duplicate";
        }

        return `<span class="${cls}">${i.imei} (${text})</span>`;

    }).join("");
}


// ===== PRICE INPUT =====
function bindPrice(){

    document.querySelectorAll(".price-input").forEach(input => {

        bindMoneyInput(input, () => {
            updateTotal();
        });

    });

}


// ===== TOTAL =====
function updateTotal(){

    let total = 0;

    document.querySelectorAll(".price-input").forEach(input => {

        let price = parseNumber(input.value);
        let count = groupedData[input.dataset.product]?.length || 0;

        total += price * count;
    });

    totalEl.innerText = formatVN(total) + " đ";
}


// ===== SAVE =====
document.getElementById("btnSave").addEventListener("click", async () => {

    let data = [];

    document.querySelectorAll(".price-input").forEach(input => {

        let price = parseNumber(input.value);
        let product = input.dataset.product;

        groupedData[product].forEach(i => {
            data.push({
                imei_id: i.imei_id,
                price
            });
        });

    });

    if(data.length === 0){
        alert("⚠️ Chưa có sản phẩm");
        return;
    }

    try{

        await api(API_SAVE, "POST", {
            customer_id: document.getElementById("customer").value,
            items: data
        });

        alert("✅ Đã lưu đơn!");

        textarea.value = "";
        groupedData = {};
        errorIMEI = [];
        render();

    }catch(e){
        alert("❌ " + e.message);
    }

});


// ===== UTILS =====
function debounce(fn, delay){
    let t;
    return (...args)=>{
        clearTimeout(t);
        t = setTimeout(()=>fn(...args), delay);
    };
}