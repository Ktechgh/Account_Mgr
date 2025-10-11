document.addEventListener("DOMContentLoaded", function () {
  const goBackButton = document.getElementById("go-back-btn");

  if (goBackButton) {
    goBackButton.addEventListener("click", function () {
      window.history.back();
    });
  }
});
