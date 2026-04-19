// ===== API WRAPPER =====
async function api(url, method="GET", data=null){
    const res = await fetch(url, {
        method,
        headers: {"Content-Type":"application/json"},
        body: data ? JSON.stringify(data) : null
    });

    let json = {};
    try { json = await res.json(); } catch {}

    if(!res.ok){
        throw new Error(json.message || "Lỗi hệ thống");
    }

    return json;
}

// ===== FORMAT =====
function formatVN(num){
    return new Intl.NumberFormat('vi-VN').format(num || 0);
}

function parseNumber(val){
    return parseInt((val || "").replace(/\D/g,'')) || 0;
}

// ===== INPUT MONEY =====
function bindMoneyInput(input, callback){
    input.addEventListener("input", function(){

        let raw = this.value.replace(/\D/g,'');
        this.value = formatVN(raw);

        if(callback) callback(raw);
    });
}