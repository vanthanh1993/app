// ===== LOAD SERVER QR =====
async function loadQR(){

    try{
        const res = await fetch("/api/server-ip");
        const data = await res.json();

        const url = location.protocol + "//" + data.ip + ":" + location.port;

        document.getElementById("urlText").innerText = url;

        QRCode.toCanvas(
            document.getElementById("qrCanvas"),
            url,
            { width: 130 }
        );

    }catch(e){
        console.error("QR error:", e);
    }

}


// AUTO LOAD
document.addEventListener("DOMContentLoaded", loadQR);