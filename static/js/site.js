window.addEventListener("DOMContentLoaded", () => {
  if (window.lucide) window.lucide.createIcons();

  const toggle = document.querySelector("[data-menu-toggle]");
  const nav = document.querySelector("#nav");
  const header = document.querySelector("[data-site-header]");
  if (toggle && nav) {
    toggle.addEventListener("click", () => nav.classList.toggle("open"));
    nav.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => nav.classList.remove("open")));
  }

  function updateHeader() {
    if (!header) return;
    header.classList.toggle("scrolled", window.scrollY > 24);
  }
  updateHeader();
  window.addEventListener("scroll", updateHeader, { passive: true });

  const stats = document.querySelector("[data-stats]");
  if (stats) {
    const counters = stats.querySelectorAll("[data-count]");
    const animateCounters = () => {
      counters.forEach((counter) => {
        const target = Number(counter.dataset.count || 0);
        const suffix = target >= 500 ? "+" : "";
        const duration = 1200;
        const start = performance.now();
        const step = (now) => {
          const progress = Math.min((now - start) / duration, 1);
          const value = Math.floor(target * (1 - Math.pow(1 - progress, 3)));
          counter.textContent = `${value.toLocaleString("en-US")}${suffix}`;
          if (progress < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
      });
    };
    const observer = new IntersectionObserver((entries) => {
      if (entries.some((entry) => entry.isIntersecting)) {
        animateCounters();
        observer.disconnect();
      }
    }, { threshold: 0.35 });
    observer.observe(stats);
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
