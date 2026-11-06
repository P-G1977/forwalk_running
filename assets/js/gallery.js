// Select all gallery images
const galleryImages = document.querySelectorAll(".gallery-item img");

// Select lightbox elements
const lightbox = document.querySelector("#lightbox");
const lightboxImage = document.querySelector("#lightbox-image");
const closeButton = document.querySelector("#lightbox-close");
const prevButton = document.getElementById("lightbox-prev");
const nextButton = document.getElementById("lightbox-next");
let currentImageIndex = 0;

function showImage(index) {
    currentImageIndex = (index + galleryImages.length) % galleryImages.length;

    lightboxImage.src = galleryImages[currentImageIndex].src;
    lightboxImage.alt = galleryImages[currentImageIndex].alt;
}

function openLightbox(index) {
    showImage(index);
    lightbox.hidden = false;
    closeButton.focus();
}

// Open the lightbox when a gallery image is clicked
galleryImages.forEach((image, index) => {
    image.addEventListener("click", () => {
        openLightbox(index);
    });
});


nextButton.addEventListener("click", () => {
    showImage(currentImageIndex + 1);
});

prevButton.addEventListener("click", () => {
    showImage(currentImageIndex - 1);
});

// Close the lightbox
function closeLightbox() {
    lightbox.hidden = true;
}

closeButton.addEventListener("click", closeLightbox);