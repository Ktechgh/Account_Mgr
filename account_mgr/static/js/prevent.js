// Prevent F12 key
document.onkeydown = function (e) {
  if (e.key === "F12") {
    e.preventDefault();
  }
};

// Prevent right-click
document.addEventListener("contextmenu", function (e) {
  e.preventDefault();
});

