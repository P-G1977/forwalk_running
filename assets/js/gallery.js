// Select all gallery images
const galleryImages = document.querySelectorAll(".gallery-item img");

// Select lightbox elements
const lightbox = document.querySelector("#lightbox");
const lightboxImage = document.querySelector("#lightbox-image");
const closeButton = document.querySelector("#lightbox-close");

// Open the lightbox when a gallery image is clicked
galleryImages.forEach((image) => {
    image.addEventListener("click", () => {
        lightboxImage.src = image.src;
        lightboxImage.alt = image.alt;
        lightbox.hidden = false;
        closeButton.focus();
    });
});

// Close the lightbox
closeButton.addEventListener("click", () => {
    lightbox.hidden = true;
});