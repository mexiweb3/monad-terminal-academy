// Ping al webclient para mostrar status en vivo. Si el tunnel muere, avisa.
(async () => {
  const el = document.getElementById("status");
  if (!el) return;
  const url = document.getElementById("play")?.href;
  if (!url) return;
  try {
    // HEAD contra el origin; si tarda >4s, asumimos caído.
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), 4000);
    await fetch(url, { mode: "no-cors", signal: ctrl.signal });
    clearTimeout(t);
    el.textContent = "status: online";
    el.classList.add("ok");
  } catch {
    el.textContent = "status: tunnel down — regenerar";
    el.classList.add("down");
  }
})();
