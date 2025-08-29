document.addEventListener("DOMContentLoaded", function () {
    const cartButton = document.getElementById("cart-button");
    const selectedSizes = {};

document.querySelectorAll(".input-spinner").forEach(spinner => {
    const input = spinner.querySelector(".quantity-input");

    const plus = spinner.querySelector(".button-plus");
    const minus = spinner.querySelector(".button-minus");

    // ✅ Remove previously attached listeners by replacing the button
    const plusClone = plus.cloneNode(true);
    const minusClone = minus.cloneNode(true);

    plus.replaceWith(plusClone);
    minus.replaceWith(minusClone);

    // ✅ Add listeners to fresh buttons
    plusClone.addEventListener("click", () => {
        let val = parseInt(input.value) || 1;
        input.value = Math.min(val + 1, 10);
    });

    minusClone.addEventListener("click", () => {
        let val = parseInt(input.value) || 1;
        input.value = Math.max(val - 1, 1);
    });
});


    // ✅ Size selection
    document.querySelectorAll(".size-options").forEach(group => {
        const productId = group.dataset.productId;
        group.querySelectorAll(".size-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                group.querySelectorAll(".size-btn").forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                selectedSizes[productId] = btn.dataset.size;
            });
        });
    });

    function scrollToNavbar() {
        const navbar = document.getElementById("navbar");
        navbar.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    function blinkCartButton() {
        cartButton.classList.add("blink-cart");
        cartButton.addEventListener("click", () => {
            cartButton.classList.remove("blink-cart");
        });
    }

    // ✅ Handle Add to Cart
    document.querySelectorAll(".add-to-cart-btn").forEach((button) => {
            if (button.classList.contains("initialized")) return;
            button.classList.add("initialized");

        button.addEventListener("click", function () {
            const productId = this.dataset.productId;
            let size = this.dataset.size;

            if (!size && selectedSizes[productId]) {
                size = selectedSizes[productId];
            }

            if (!size) {
                alert("Please select a size.");
                return;
            }

            // ✅ Get quantity from closest quantity input
const quantityInput = this.closest(".modal-content")?.querySelector(".quantity-input");
const quantity = quantityInput ? parseInt(quantityInput.value) || 1 : 1;


            const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;

            fetch("/add-to-cart/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ product_id: productId, size: size, quantity: quantity })
            })
                .then((response) => {
                    if (!response.ok) throw new Error("Failed to add");
                    return response.json();
                })
                .then((data) => {
                    blinkCartButton();

                    // 👇 Close Bootstrap modal if open
                    const modal = document.querySelector(".modal.show");
                    if (modal) {
                        const modalInstance = bootstrap.Modal.getInstance(modal);
                        if (modalInstance) {
                            modalInstance.hide();
                            cartButton.focus();
                        }
                    }

                    scrollToNavbar();
                    console.log("🔁 Calling /cart/sidebar/ to refresh sidebar");
                    refreshCartSidebar();
                })
                .catch((error) => {
                    alert("Error adding to cart.");
                    console.error(error);
                });
        });
    });
});
