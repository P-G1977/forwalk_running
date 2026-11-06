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
const galleryTriggers = document.querySelectorAll(".gallery-trigger");

// State
let currentImageIndex = 0;
let previouslyFocusedElement = null;

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
    previouslyFocusedElement = document.activeElement;

    showImage(index);
    lightbox.hidden = false;
    closeButton.focus();
}

function closeLightbox() {
    lightbox.hidden = true;

    if (previouslyFocusedElement) {
        previouslyFocusedElement.focus();
    }
}

/* Event Listeners */

// Open the lightbox when a gallery button is clicked
galleryTriggers.forEach((button, index) => {
    button.addEventListener("click", () => {
        openLightbox(index);
    });
});

// Navigation buttons
nextButton.addEventListener("click", () => showImage(currentImageIndex + 1));
prevButton.addEventListener("click", () => showImage(currentImageIndex - 1));
closeButton.addEventListener("click", closeLightbox);

// Keyboard navigation
document.addEventListener("keydown", (event) => {
  if (lightbox.hidden) return;

  if (event.key === "Tab") {
    const focusableElements = [
        closeButton,
        prevButton,
        nextButton
    ];

    const currentIndex = focusableElements.indexOf(document.activeElement);

    if (event.shiftKey) {
        // Shift + Tab moves backwards
        const previousIndex =
            (currentIndex - 1 + focusableElements.length) %
            focusableElements.length;

        event.preventDefault();
        focusableElements[previousIndex].focus();
    } else {
        // Tab moves forwards
        const nextIndex =
            (currentIndex + 1) % focusableElements.length;

        event.preventDefault();
        focusableElements[nextIndex].focus();
    }
}

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