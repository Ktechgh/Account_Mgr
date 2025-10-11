// USER PROFILE DROPDOWN
const userProfile = document.querySelector(".user-profile");
userProfile.addEventListener("click", () => {
  userProfile.classList.toggle("open");
});
document.addEventListener("click", function (e) {
  if (userProfile && !userProfile.contains(e.target)) {
    userProfile.classList.remove("open");
  }
});

// TOGGLE SIDEBAR
const sidebar = document.querySelector(".sidebar");
const toggleSidebar = document.querySelector(".toggle-sidebar");
const mainSection = document.querySelector(".main-section");

// Toggle sidebar when clicking the toggle button
toggleSidebar.addEventListener("click", () => {
  sidebar.classList.toggle("closed");
  mainSection.classList.toggle("sidebar-closed");
});

// Close sidebar when clicking outside of it
document.addEventListener("click", (e) => {
  const isClickInsideSidebar = sidebar.contains(e.target);
  const isClickOnToggle = toggleSidebar.contains(e.target);

  if (!isClickInsideSidebar && !isClickOnToggle) {
    sidebar.classList.remove("closed");
    mainSection.classList.remove("sidebar-closed");
  }
});

// SUBMENU TOGGLE (Accordion behavior)
const submenuParents = document.querySelectorAll(".has-submenu");
submenuParents.forEach((parentLi) => {
  const menuLink = parentLi.querySelector("a");
  menuLink.addEventListener("click", (e) => {
    e.preventDefault();
    // Close other submenus
    submenuParents.forEach((otherLi) => {
      if (otherLi !== parentLi) {
        otherLi.classList.remove("open");
      }
    });
    // Toggle current submenu
    parentLi.classList.toggle("open");
  });
});

// On page load, check localStorage and apply the theme
if (localStorage.getItem("theme") === "dark") {
  document.body.classList.add("dark-theme");
} else {
  document.body.classList.remove("dark-theme");
}

const themeToggle = document.getElementById("theme-toggle");
themeToggle.addEventListener("click", (e) => {
  e.preventDefault();
  document.body.classList.toggle("dark-theme");
  if (document.body.classList.contains("dark-theme")) {
    localStorage.setItem("theme", "dark");
  } else {
    localStorage.setItem("theme", "light");
  }
});


// Show the button when the user scrolls down 20px from the top of the page
function scrollFunction() {
  const scrollBtn = document.getElementById("scrollTopBtn");
  if (!scrollBtn) return; 

  if (window.scrollY > 20) scrollBtn.style.display = "block";
  else scrollBtn.style.display = "none";
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: "smooth" });
}

document.addEventListener("DOMContentLoaded", () => {
  const scrollBtn = document.getElementById("scrollTopBtn");
  if (!scrollBtn) return;

  window.addEventListener("scroll", scrollFunction);
  scrollBtn.addEventListener("click", scrollToTop);

  scrollFunction();
});
