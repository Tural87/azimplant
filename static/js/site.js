window.addEventListener("DOMContentLoaded", () => {
  if (window.lucide) window.lucide.createIcons();

  const toggle = document.querySelector("[data-menu-toggle]");
  const nav = document.querySelector("#nav");
  if (toggle && nav) {
    toggle.addEventListener("click", () => nav.classList.toggle("open"));
    nav.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => nav.classList.remove("open")));
  }

  const waLink = document.querySelector("[data-whatsapp-link]");
  const floatingWhatsApp = document.querySelector("[data-floating-whatsapp]");
  const defaultText = encodeURIComponent("Salam, Az Implant Group haqqinda melumat almaq isteyirem.");

  if (waLink) {
    waLink.addEventListener("click", (event) => {
      event.preventDefault();
      floatingWhatsApp?.click();
    });
  }

  if (floatingWhatsApp) {
    const separator = floatingWhatsApp.href.includes("?") ? "&" : "?";
    floatingWhatsApp.href = `${floatingWhatsApp.href}${separator}text=${defaultText}`;
  }
});
