// Mobile menu toggle
const menuBtn = document.getElementById("menu-btn");
const navLinks = document.getElementById("nav-links");
if (menuBtn && navLinks) {
  const setMenuOpen = isOpen => {
    navLinks.classList.toggle("open", isOpen);
    menuBtn.setAttribute("aria-expanded", String(isOpen));
    menuBtn.setAttribute("aria-label", isOpen ? "Close navigation menu" : "Open navigation menu");
  };

  menuBtn.addEventListener("click", () => {
    setMenuOpen(!navLinks.classList.contains("open"));
  });

  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && navLinks.classList.contains("open")) {
      setMenuOpen(false);
      menuBtn.focus();
    }
  });
}

// Show a preview of the chosen garbage image on the report page
const imageInput = document.getElementById("image");
if (imageInput) imageInput.addEventListener("change", () => {
  const preview = document.getElementById("preview"), file = imageInput.files[0];
  if (file) { preview.src = URL.createObjectURL(file); preview.style.display = "block"; } else preview.style.display = "none";
});

// Hide flash messages after 5 seconds
setTimeout(() => document.querySelectorAll(".alert").forEach(a => a.style.display = "none"), 5000);
