// ===== REMOVE ITEM =====
async function removeItem(id){

    if(!confirmDelete("Xoá IMEI này?")) return;

    try{

        await api(`/sale/remove-imei/${id}`, "POST");

        document.querySelector(`tr[data-id="${id}"]`)?.remove();

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

            await api(`/sale/update-price/${id}`, "POST", {
                price: raw
            });

            updateTotal();

        }catch(e){
            toast(e.message, false);
        }

    });

});


// ===== UPDATE TOTAL =====
async function updateTotal(){

    try{

        const data = await api(`/sale/update-total/${saleId}`);

        document.getElementById("total").innerText =
            formatVN(data.total);

    }catch(e){
        console.error(e);
    }

}