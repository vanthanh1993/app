document.addEventListener("DOMContentLoaded", () => {

    const textarea = document.getElementById("imei_input");
    const listDiv = document.getElementById("list");
    const totalEl = document.getElementById("total");
    const emptyEl = document.getElementById("empty");
    const saveBtn = document.getElementById("saveBtn");

    let groupedData = {};
    let errorIMEI = [];
    let debounce;

    // ===== INPUT =====
    textarea.addEventListener("input", () => {

        clearTimeout(debounce);

        debounce = setTimeout(async () => {

            let imeis = textarea.value.split("\n")
                .map(x => x.trim())
                .filter(x => x);

            if (imeis.length === 0) {
                groupedData = {};
                errorIMEI = [];
                render();
                return;
            }

            const res = await fetch("/sale/check-imei", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ imeis })
            });

            const data = await res.json();

            groupedData = {};
            errorIMEI = [];

            data.forEach(i => {

                if (i.status !== "ok") {
                    errorIMEI.push(i);
                    return;
                }

                if (!groupedData[i.product]) {
                    groupedData[i.product] = [];
                }

                groupedData[i.product].push(i);
            });

            render();

        }, 300);
    });

    // ===== RENDER =====
    function render() {

        listDiv.innerHTML = "";
        renderStatus();

        if (Object.keys(groupedData).length === 0) {
            emptyEl.style.display = "block";
            updateTotal();
            return;
        }

        emptyEl.style.display = "none";

        for (let product in groupedData) {

            let group = groupedData[product];

            listDiv.innerHTML += `
            <div class="card card-product shadow-sm">
                <div class="card-body p-2">

                    <div class="d-flex justify-content-between align-items-center">

                        <div>
                            <b>${product}</b>
                            <div class="small text-muted">
                                đã chọn : ${group.length} imei
                            </div>
                        </div>

                        <input class="form-control text-end price-input"
                            placeholder="Giá"
                            data-product="${product}">
                    </div>

                    <div class="mt-2">
                        ${group.map(i => `
                            <span class="badge badge-imei me-1 mb-1">
                                ${i.imei}
                            </span>
                        `).join("")}
                    </div>

                </div>
            </div>`;
        }

        bindPriceInput();
    }

    // ===== STATUS =====
    function renderStatus() {

        const box = document.getElementById("imeiStatus");

        if (errorIMEI.length === 0) {
            box.innerHTML = "";
            return;
        }

        box.innerHTML = errorIMEI.map(i => {

            let cls = "status-notfound";
            let text = "Không tồn tại";

            if (i.status === "sold") {
                cls = "status-sold";
                text = "Đã bán";
            } else if (i.status === "duplicate") {
                cls = "status-duplicate";
                text = "Trùng";
            }

            return `<span class="${cls}">${i.imei} (${text})</span>`;

        }).join("");
    }

    // ===== PRICE (FIX CURSOR) =====
    function bindPriceInput() {

        document.querySelectorAll(".price-input").forEach(input => {

            input.addEventListener("input", function () {

                let inputEl = this;
                let start = inputEl.selectionStart;

                let left = inputEl.value.slice(0, start);
                let digitsBefore = left.replace(/\D/g, '').length;

                let raw = inputEl.value.replace(/\D/g, '');

                if (raw.length === 0) {
                    inputEl.value = "";
                    updateTotal();
                    return;
                }

                let formatted = new Intl.NumberFormat("vi-VN").format(raw);

                inputEl.value = formatted;

                requestAnimationFrame(() => {

                    let pos = formatted.length;
                    let count = 0;

                    for (let i = 0; i < formatted.length; i++) {
                        if (/\d/.test(formatted[i])) count++;

                        if (count >= digitsBefore) {
                            pos = i + 1;
                            break;
                        }
                    }

                    inputEl.setSelectionRange(pos, pos);
                });

                updateTotal();
            });

        });
    }

    // ===== TOTAL =====
    function updateTotal() {

        let total = 0;

        document.querySelectorAll(".price-input").forEach(input => {

            let price = parseInt(input.value.replace(/\D/g, '')) || 0;
            let product = input.dataset.product;

            let count = groupedData[product]?.length || 0;

            total += price * count;
        });

        totalEl.innerText =
            new Intl.NumberFormat("vi-VN").format(total) + " đ";
    }

    // ===== SAVE =====
    saveBtn.addEventListener("click", async () => {

        let data = [];

        document.querySelectorAll(".price-input").forEach(input => {

            let price = parseInt(input.value.replace(/\D/g, '')) || 0;
            let product = input.dataset.product;

            groupedData[product].forEach(i => {
                data.push({
                    imei_id: i.imei_id,
                    price
                });
            });
        });

        if (data.length === 0) {
            alert("⚠️ Chưa có sản phẩm");
            return;
        }

        const res = await fetch("/sale", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                customer_id: document.getElementById("customer").value,
                items: data
            })
        });

        const result = await res.json();

        if (!res.ok) {
            alert("❌ " + result.message);
            return;
        }

        alert("✅ Đã lưu đơn!");

        textarea.value = "";
        groupedData = {};
        errorIMEI = [];
        render();
    });

});