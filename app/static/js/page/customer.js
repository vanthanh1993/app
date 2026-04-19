let deleteId = null;

// VALIDATE
function validateCustomerForm(){
    const f = document.getElementById("customerForm");

    const name = f.name.value.trim();
    const phone = f.phone.value.trim();
    const address = f.address.value.trim();

    if(!name && !phone && !address){
        toast("Nhập ít nhất 1 thông tin", false);
        return false;
    }

    return {name, phone, address};
}

// ADD
document.getElementById("customerForm")?.addEventListener("submit", e=>{
    if(!validateCustomerForm()) e.preventDefault();
});

// SEARCH
document.getElementById("btnSearch")?.addEventListener("click", ()=>{
    const data = validateCustomerForm();
    if(!data) return;

    window.location.href = "/customer/search?" + new URLSearchParams(data);
});

// EVENT
document.addEventListener("click", function(e){

    // EDIT
    const edit = e.target.closest(".edit-btn");
    if(edit){
        const id = edit.dataset.id;

        editName.value = edit.dataset.name;
        editPhone.value = edit.dataset.phone;
        editAddress.value = edit.dataset.address;

        editForm.action = "/customer/edit/" + id;

        showModal("editModal");
    }

    // DELETE
    const del = e.target.closest(".delete-btn");
    if(del){
        deleteId = del.dataset.id;
        showModal("deleteModal");
    }
});

// CONFIRM DELETE
document.getElementById("confirmDeleteBtn")?.addEventListener("click", async function(){

    if(!deleteId) return;

    try{
        await api("/customer/delete/" + deleteId, "POST");

        document.getElementById("row-"+deleteId)?.remove();
        toast("Đã xoá");

        hideModal("deleteModal");

    }catch(e){
        toast(e.message, false);
    }
});