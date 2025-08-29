if (
  document.querySelector("#productModal") &&
  document.querySelector("#productModalThumbnails")
) {
  modalSlider = tns({
    container: "#productModal",
    items: 1,
    startIndex: 0,
    navContainer: "#productModalThumbnails",
    navAsThumbnails: true,
    autoplay: false,
    autoplayTimeout: 1500,
    swipeAngle: false,
    speed: 1500,
    controls: false,
    autoplayButtonOutput: false,
    loop: false
  });
}

1<document.querySelectorAll(".product")
.length&&(productSlider=tns(
    {container:"#product",
        items:1,
        startIndex:0,
        navContainer:"#productThumbnails",
        navAsThumbnails:!0,
        autoplay:!1,
        autoplayTimeout:1500,
        swipeAngle:!1,
        speed:1500,
        controls:!1,
        autoplayButtonOutput:!1}));