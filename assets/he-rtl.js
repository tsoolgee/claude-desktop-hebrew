/* claude-desktop-hebrew: flips the page to RTL while the UI language is Hebrew. */
(function () {
  function locale() {
    try { return localStorage.getItem("spa:locale") || navigator.language || ""; } catch (e) { return navigator.language || ""; }
  }
  function apply() {
    var he = /^he(-|$)/i.test(locale());
    var root = document.documentElement;
    if (he) {
      if (root.dir !== "rtl") root.dir = "rtl";
      if (root.lang !== "he") root.lang = "he";
    } else if (root.dataset.heApplied === "1") {
      root.dir = "ltr";
    }
    root.dataset.heApplied = he ? "1" : "0";
  }
  apply();
  setInterval(apply, 800);
  window.addEventListener("storage", apply);
})();
