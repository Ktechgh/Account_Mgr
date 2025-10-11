document.addEventListener("DOMContentLoaded", function () {
  // Countdown Timer Logic
  let timeLeft = 40; // You can adjust the time
  const countdownElement = document.getElementById("countdown");
  const retryButton = document.getElementById("retry-btn");

  if (countdownElement) {
    const countdown = setInterval(() => {
      timeLeft--;
      countdownElement.innerText = timeLeft;

      if (timeLeft <= 0) {
        clearInterval(countdown);
        document.querySelector(".timer").innerHTML =
          "<p>You can try again now.</p>";
      }
    }, 1000);
  } else {
    console.error("Element with id 'countdown' not found.");
  }

  // Retry button logic
  if (retryButton) {
    retryButton.addEventListener("click", function () {
      location.reload(); // Reloads the page after countdown finishes
    });
  }
});
