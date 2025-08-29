document.addEventListener("DOMContentLoaded", function () {
  function refreshCartSidebar() {
    console.log("🔁 Calling /cart/sidebar/ to refresh sidebar");

    fetch("/cart/sidebar/")
      .then((response) => {
        if (!response.ok) throw new Error("Failed to load cart sidebar");
        return response.text();
      })
      .then((html) => {
        const cartSidebarBody = document.getElementById("cartSidebarBody");
        if (cartSidebarBody) {
          cartSidebarBody.innerHTML = html;
        } else {
          console.warn("❌ #cartSidebarBody element not found");
        }
      })
      .catch((err) => console.error("Error refreshing cart sidebar:", err));
  }

  function addToCart(productId, size, quantity) {
    fetch("/add-to-cart/", {
      method: "POST",
      headers: {
        "X-CSRFToken": csrfToken,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ product_id: productId, size: size, quantity: quantity }),
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to add item to cart");
        return res.json();
      })
      .then((data) => {
        if (data.success) {
          const modalEl = document.querySelector(".modal.show");
          if (modalEl) {
            const bsModal = bootstrap.Modal.getInstance(modalEl);
            if (bsModal) bsModal.hide();
          }

          scrollToNavbar();
          blinkCartButton();
          refreshCartSidebar(); // ✅ Refresh sidebar
        } else {
          alert(data.error || "Error adding to cart.");
        }
      })
      .catch((err) => {
        console.error("Add to cart error:", err);
        alert("There was an error adding the product to your cart.");
      });
  }

  const cartOffcanvas = document.getElementById("offcanvasRight");

  if (cartOffcanvas) {
    cartOffcanvas.addEventListener("show.bs.offcanvas", function () {
      refreshCartSidebar(); // 🔁 Load fresh cart every time it's opened
    });
  }

  // Expose addToCart globally if needed
  window.addToCart = addToCart;
});
