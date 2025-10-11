document.addEventListener("DOMContentLoaded", function () {
  const goBackButton = document.getElementById("go-back-btn");

  if (goBackButton) {
    goBackButton.addEventListener("click", function () {
      window.history.back();
    });
  }
});

// 500 server
document.addEventListener("DOMContentLoaded", function () {
  const refreshBtn = document.getElementById("server_refresh-btn");

  if (refreshBtn) {
    refreshBtn.addEventListener("click", function () {
      location.reload();
    });
  }
});
