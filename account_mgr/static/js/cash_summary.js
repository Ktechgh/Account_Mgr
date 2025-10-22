document.addEventListener("DOMContentLoaded", function () {
  const viewModeSelect = document.getElementById("viewMode");
  const oldView = document.getElementById("oldView");
  const newView = document.getElementById("newView");

  // ✅ Only run if the Cash Summary elements exist
  if (viewModeSelect && oldView && newView) {
    // Default: show only the old/original summary on load
    oldView.style.display = "block";
    newView.style.display = "none";
    viewModeSelect.value = "old";

    // Toggle visibility when user changes selection
    viewModeSelect.addEventListener("change", function () {
      const mode = this.value;
      if (mode === "old") {
        oldView.style.display = "block";
        newView.style.display = "none";
      } else {
        oldView.style.display = "none";
        newView.style.display = "block";
      }
    });
  }
});
