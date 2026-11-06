/* DOM References & State */

// Gallery images
const galleryImages = document.querySelectorAll(".gallery-item img");

// Lightbox elements
const lightbox = document.querySelector("#lightbox");
const lightboxImage = document.querySelector("#lightbox-image");
const closeButton = document.getElementById("lightbox-close");
const prevButton = document.getElementById("lightbox-prev");
const nextButton = document.getElementById("lightbox-next");
const lightboxCounter = document.getElementById("lightbox-counter");

// State
let currentImageIndex = 0;

/* Core Functions */

function showImage(index) {
  // Wrap around using modulo so index stays within bounds
  currentImageIndex = (index + galleryImages.length) % galleryImages.length;
  lightboxImage.src = galleryImages[currentImageIndex].src;
  lightboxImage.alt = galleryImages[currentImageIndex].alt;
  lightboxCounter.textContent =
    `${currentImageIndex + 1} / ${galleryImages.length}`;
}

function openLightbox(index) {
  showImage(index);
  lightbox.hidden = false;
  closeButton.focus();
}

function closeLightbox() {
  lightbox.hidden = true;
}

/* Event Listeners */

// Open the lightbox when a gallery image is clicked
galleryImages.forEach((image, index) => {
  image.addEventListener("click", () => openLightbox(index));
});

// Navigation buttons
nextButton.addEventListener("click", () => showImage(currentImageIndex + 1));
prevButton.addEventListener("click", () => showImage(currentImageIndex - 1));
closeButton.addEventListener("click", closeLightbox);

// Keyboard navigation
document.addEventListener("keydown", (event) => {
  if (lightbox.hidden) return;

  switch (event.key) {
    case "ArrowRight":
      event.preventDefault();
      showImage(currentImageIndex + 1);
      break;
    case "ArrowLeft":
      event.preventDefault();
      showImage(currentImageIndex - 1);
      break;
    case "Escape":
      closeLightbox();
      break;
  }
});