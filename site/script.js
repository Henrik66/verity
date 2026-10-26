// Easter egg: a small smiley trails the cursor around the hero.
// Skipped for touch screens and for people who prefer reduced motion.
(function () {
  const follower = document.querySelector(".follower");
  const hero = document.querySelector(".hero");
  if (!follower || !hero) return;
  if (!matchMedia("(pointer: fine)").matches) return;
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  let x = 0, y = 0, fx = 0, fy = 0, raf = 0;

  function step() {
    fx += (x - fx) * 0.12;
    fy += (y - fy) * 0.12;
    const tilt = Math.max(-25, Math.min(25, (x - fx) * 0.6));
    follower.style.transform = `translate(${fx + 14}px, ${fy + 14}px) rotate(${tilt}deg)`;
    raf = requestAnimationFrame(step);
  }

  hero.addEventListener("pointerenter", (e) => {
    x = fx = e.clientX;
    y = fy = e.clientY;
    follower.classList.add("on");
    if (!raf) raf = requestAnimationFrame(step);
  });
  hero.addEventListener("pointermove", (e) => {
    x = e.clientX;
    y = e.clientY;
  });
  hero.addEventListener("pointerleave", () => {
    follower.classList.remove("on");
    cancelAnimationFrame(raf);
    raf = 0;
  });
})();
