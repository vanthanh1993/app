function deleteSupplier(id){
    if(!confirmDelete("Xoá NCC?")) return;

    fetch("/supplier/delete/" + id, {
        method: "POST"
    }).then(()=> location.reload());
}