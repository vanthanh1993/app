// ===== REMOVE IMEI =====
async function removeIMEI(itemId){

    if(!confirmDelete("Xoá IMEI này?")) return;

    try{

        await api(`/purchase/remove-imei/${itemId}`, "POST");

        document.querySelector(`tr[data-id="${itemId}"]`)?.remove();

        updateTotal();

        toast("Đã xoá");

    }catch(e){
        toast(e.message, false);
    }
}


// ===== UPDATE PRICE =====
document.querySelectorAll(".price-input").forEach(input => {

    bindMoneyInput(input, async raw => {

        const id = input.dataset.id;

        try{

            await api(`/purchase/update-price/${id}`, "POST", {
                price: raw
            });

            updateTotal();

        }catch(e){
            toast(e.message, false);
        }

    });

});


// ===== UPDATE IMEI =====
document.querySelectorAll(".imei-input").forEach(input => {

    input.addEventListener("change", async function(){

        const id = input.dataset.id;
        const imei = input.value.trim();

        if(!imei){
            toast("IMEI không được trống", false);
            return;
        }

        try{

            await api(`/purchase/update-imei/${id}`, "POST", {
                imei
            });

            toast("Đã cập nhật IMEI");

        }catch(e){
            toast(e.message, false);
        }

    });

});


// ===== UPDATE TOTAL =====
async function updateTotal(){

    try{

        const data = await api(`/purchase/update-total/${purchaseId}`);

        document.getElementById("total").innerText =
            formatVN(data.total);

    }catch(e){
        console.error(e);
    }

}