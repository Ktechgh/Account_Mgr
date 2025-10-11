let logoutTimer;
let warningTimer;

function resetTimer() {
  clearTimeout(logoutTimer);
  clearTimeout(warningTimer);

  // Set logout for 5 minutes
  // logoutTimer = setTimeout(logout, 300000); // 5 mins = 300,000 ms

  // Set logout for 15 minutes
  logoutTimer = setTimeout(logout, 900000); // 15 mins = 900,000 ms


  // Show alert at 4.5 minutes
  warningTimer = setTimeout(showWarning, 270000); // 4.5 mins = 270,000 ms
}

function showWarning() {
  alert("You will be logged out in 30 seconds due to inactivity.");
  // Note: This doesn't cancel logout, just informs the user.
}

function logout() {
  const logoutUrl = document.body.getAttribute("data-logout-url");
  if (logoutUrl) {
    window.location.href = logoutUrl;
  }
}

// Listen to user activity
document.addEventListener("DOMContentLoaded", resetTimer);
document.addEventListener("mousemove", resetTimer);
document.addEventListener("keypress", resetTimer);
document.addEventListener("click", resetTimer);
document.addEventListener("scroll", resetTimer);
