const amountInput = document.getElementById("amount");

bindMoneyInput(amountInput);

document.getElementById("btnPay").addEventListener("click", async () => {

    let amount = parseNumber(amountInput.value);
    let note = document.getElementById("note").value;

    if(amount <= 0){
        toast("Số tiền không hợp lệ", false);
        return;
    }

    try{
        await api(API_PAY, "POST", { amount, note });

        toast("Đã thanh toán");
        location.reload();

    }catch(e){
        toast(e.message, false);
    }
});