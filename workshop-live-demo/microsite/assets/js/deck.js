// ShopBot Workshop deck — Reveal.js bootstrap + lab countdown timers.
// Vanilla JS, no build step, works fully offline.

(function () {
  "use strict";

  function initReveal() {
    Reveal.initialize({
      hash: true,
      controls: true,
      progress: true,
      center: true,
      transition: "slide",
      width: 1280,
      height: 720,
      margin: 0.06,
      plugins: [RevealNotes, RevealHighlight, RevealZoom],
    });
  }

  // ---- Countdown timer component -----------------------------------
  // Usage: <div class="countdown" data-minutes="30"> ... </div>
  // with a child .countdown-digits span and buttons data-action="start|pause|reset"

  function formatTime(totalSeconds) {
    const m = Math.floor(totalSeconds / 60);
    const s = totalSeconds % 60;
    return String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0");
  }

  function setupCountdown(el) {
    const startMinutes = parseFloat(el.dataset.minutes || "30");
    let remaining = Math.round(startMinutes * 60);
    let intervalId = null;

    const digits = el.querySelector(".countdown-digits");

    function render() {
      digits.textContent = formatTime(Math.max(remaining, 0));
      el.classList.remove("warning", "expired");
      if (remaining <= 0) {
        el.classList.add("expired");
      } else if (remaining <= 300) {
        el.classList.add("warning");
      }
    }

    function tick() {
      remaining -= 1;
      render();
      if (remaining <= 0) {
        clearInterval(intervalId);
        intervalId = null;
      }
    }

    function start() {
      if (intervalId) return;
      intervalId = setInterval(tick, 1000);
    }

    function pause() {
      if (intervalId) {
        clearInterval(intervalId);
        intervalId = null;
      }
    }

    function reset() {
      pause();
      remaining = Math.round(startMinutes * 60);
      render();
    }

    el.querySelectorAll("[data-action]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const action = btn.dataset.action;
        if (action === "start") start();
        if (action === "pause") pause();
        if (action === "reset") reset();
      });
    });

    render();
  }

  function initCountdowns() {
    document.querySelectorAll(".countdown[data-minutes]").forEach(setupCountdown);
  }

  document.addEventListener("DOMContentLoaded", function () {
    initReveal();
    initCountdowns();
  });
})();
