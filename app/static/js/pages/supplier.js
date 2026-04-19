document.addEventListener("DOMContentLoaded", () => {

    const modal = new bootstrap.Modal(document.getElementById("editModal"));

    document.querySelectorAll(".edit-btn").forEach(btn => {

        btn.addEventListener("click", () => {

            const id = btn.dataset.id;

            document.getElementById("editName").value = btn.dataset.name;
            document.getElementById("editPhone").value = btn.dataset.phone;
            document.getElementById("editAddress").value = btn.dataset.address;

            document.getElementById("editForm").action = `/supplier/edit/${id}`;

            modal.show();
        });
    });

});

