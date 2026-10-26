// Mobile contents drawer and "on this page" highlighting.
(function () {
  const btn = document.querySelector(".menu-btn");
  const sidebar = document.getElementById("sidebar");
  if (btn && sidebar) {
    const set = (open) => {
      sidebar.classList.toggle("open", open);
      btn.setAttribute("aria-expanded", String(open));
    };
    btn.addEventListener("click", () => set(!sidebar.classList.contains("open")));
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && sidebar.classList.contains("open")) {
        set(false);
        btn.focus();
      }
    });
    sidebar.addEventListener("click", (e) => {
      if (e.target.closest("a")) set(false);
    });
  }

  const links = [...document.querySelectorAll(".on-page a")];
  if (!links.length || !("IntersectionObserver" in window)) return;
  const byId = new Map(links.map((a) => [a.hash.slice(1), a]));
  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        links.forEach((a) => a.classList.remove("active"));
        byId.get(entry.target.id)?.classList.add("active");
      }
    },
    { rootMargin: "-60px 0px -70% 0px" }
  );
  byId.forEach((_, id) => {
    const h = document.getElementById(id);
    if (h) observer.observe(h);
  });
})();
