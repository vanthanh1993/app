// ===== TOAST =====
function toast(msg, ok=true){
    const t = document.getElementById('toast');
    const body = document.getElementById('toastMsg');

    if(!t || !body){
        alert(msg);
        return;
    }

    body.innerText = msg;

    t.className = "toast border-0 " + (ok ? "text-bg-success" : "text-bg-danger");

    bootstrap.Toast.getOrCreateInstance(t).show();
}

// ===== CONFIRM =====
function confirmDelete(msg="Bạn có chắc?"){
    return confirm(msg);
}

// ===== MODAL =====
function showModal(id){
    bootstrap.Modal.getOrCreateInstance(document.getElementById(id)).show();
}

function hideModal(id){
    bootstrap.Modal.getInstance(document.getElementById(id))?.hide();
}