const darkModeToggle = document.getElementById("dark-mode-toggle");
const mainContainer = document.querySelector(".container-fluid");

window.addEventListener("DOMContentLoaded", () => {
  const darkMode = localStorage.getItem("darkMode");

  if (darkMode === "enabled") {
    mainContainer.classList.add("dark-mode");
    darkModeToggle.checked = true;
  }
});

darkModeToggle.addEventListener("change", () => {
  if (darkModeToggle.checked) {
    mainContainer.classList.add("dark-mode");
    localStorage.setItem("darkMode", "enabled");
  } else {
    mainContainer.classList.remove("dark-mode");
    localStorage.setItem("darkMode", "disabled");
  }
});
