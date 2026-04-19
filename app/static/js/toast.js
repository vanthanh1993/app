document.addEventListener("DOMContentLoaded", () => {

    const container = document.getElementById("toastContainer");

    function showToast(message, type = "success") {

        let bg = "bg-success";

        if (type === "danger") bg = "bg-danger";
        if (type === "warning") bg = "bg-warning";
        if (type === "info") bg = "bg-info";

        const el = document.createElement("div");

        el.className = `toast align-items-center text-white ${bg} border-0 show mb-2`;
        el.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto"></button>
            </div>
        `;

        container.appendChild(el);

        // auto remove
        setTimeout(() => el.remove(), 3000);

        // close btn
        el.querySelector("button").onclick = () => el.remove();
    }

    // 🔥 load flash từ backend
    if (window.FLASH_MESSAGES) {
        window.FLASH_MESSAGES.forEach(([type, msg]) => {
            showToast(msg, type);
        });
    }

    // expose global
    window.showToast = showToast;

});