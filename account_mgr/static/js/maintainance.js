document.addEventListener("DOMContentLoaded", function () {
  setInterval(function () {
    window.location.reload();
  }, 60000);

  const reloadBtn = document.getElementById("main-reload-btn");
  if (reloadBtn) {
    reloadBtn.addEventListener("click", function () {
      window.location.reload();
    });
  }
});
