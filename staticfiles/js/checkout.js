document.addEventListener("DOMContentLoaded", () => {
  const confirmBtn = document.getElementById("confirmOrderBtn");
  if (confirmBtn) {
    confirmBtn.addEventListener("click", handleConfirmOrder);
  }
});

function handleConfirmOrder() {
  console.log("🟢 Confirm clicked");

  fetch("/checkout/confirm-order/", {
    method: "POST",
    headers: {
      "X-CSRFToken": csrfToken,
      "Content-Type": "application/json",
    },
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        alert("✅ Order placed successfully!");
        refreshCartSidebar();
        document.getElementById("checkoutDetails").innerHTML = "";
        bootstrap.Modal.getInstance(document.getElementById("orderSummaryModal")).hide();
      } else {
        alert("⚠️ " + data.error);
      }
    })
    .catch((err) => {
      console.error("❌ Error confirming order:", err);
      alert("Something went wrong");
    });
}
