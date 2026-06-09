window.addEventListener("DOMContentLoaded", () => {
  if (window.lucide) window.lucide.createIcons();

  const toggle = document.querySelector("[data-menu-toggle]");
  const nav = document.querySelector("#nav");
  if (toggle && nav) {
    toggle.addEventListener("click", () => nav.classList.toggle("open"));
    nav.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => nav.classList.remove("open")));
  }

  const form = document.querySelector("[data-wa-form]");
  const waButton = document.querySelector("[data-wa-submit]");
  const waLink = document.querySelector("[data-whatsapp-link]");
  const number = form?.dataset.waNumber || "";

  function buildWhatsAppUrl() {
    const data = new FormData(form);
    const text = [
      "Az Implant Group müraciət",
      `Ad: ${data.get("first_name") || ""}`,
      `Soyad: ${data.get("last_name") || ""}`,
      `Email: ${data.get("email") || ""}`,
      `Nömrə: ${data.get("phone") || ""}`,
      `Mesaj: ${data.get("message") || ""}`,
    ].join("\n");
    return `https://wa.me/${number}?text=${encodeURIComponent(text)}`;
  }

  if (waButton && form) {
    waButton.addEventListener("click", () => {
      if (!form.reportValidity()) return;
      window.open(buildWhatsAppUrl(), "_blank", "noopener");
    });
  }

  if (waLink && number) {
    waLink.addEventListener("click", (event) => {
      event.preventDefault();
      window.location.hash = "contact";
    });
  }
});
