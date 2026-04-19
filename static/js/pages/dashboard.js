
document.addEventListener("DOMContentLoaded", async () => {
    const canvas = document.getElementById("qrCanvas");
    if (!canvas || typeof QRCode === "undefined") return;

    let url = window.location.origin;

    // nếu local thì dùng IP LAN
    if (url.includes("127.0.0.1") || url.includes("localhost")) {
        try {
            const res = await fetch("/api/server-ip");
            const data = await res.json();
            url = `http://${data.ip}:5000`;
        } catch {}
    }

    document.getElementById("urlText").innerText = url;
    QRCode.toCanvas(canvas, url, { width: 130 });
});


function copyLink() {
    const text = document.getElementById("urlText").innerText;
    const btn = document.getElementById("copyBtn");

    if (!text) return;

    if (navigator.clipboard) {
        navigator.clipboard.writeText(text);
    } else {
        const input = document.createElement("input");
        input.value = text;
        document.body.appendChild(input);
        input.select();
        document.execCommand("copy");
        document.body.removeChild(input);
    }

    btn.innerHTML = "✅ Đã copy";

    setTimeout(() => {
        btn.innerHTML = '<i class="bi bi-clipboard"></i> Copy';
    }, 1500);
}