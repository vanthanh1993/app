function filterRows(){

    let search = document.getElementById("search").value.toLowerCase();
    let supplier = document.getElementById("supplier_filter").value;

    document.querySelectorAll("[data-id]").forEach(el => {

        let ok1 = el.dataset.id.includes(search);
        let ok2 = !supplier || el.dataset.supplier == supplier;

        el.style.display = (ok1 && ok2) ? "" : "none";
    });
}

let t;
function debounceFilter(){
    clearTimeout(t);
    t = setTimeout(filterRows, 200);
}

document.getElementById("search").addEventListener("input", debounceFilter);
document.getElementById("supplier_filter").addEventListener("change", filterRows);