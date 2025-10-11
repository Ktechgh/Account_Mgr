document.addEventListener("DOMContentLoaded", function () {
  const flashMessages = document.querySelectorAll(".flash--message .alert");

  flashMessages.forEach(function (message) {
    const totalAnimationTime = 4000;

    setTimeout(function () {
      message.remove();
    }, totalAnimationTime);
  });
});
