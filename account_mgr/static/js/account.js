document.addEventListener("DOMContentLoaded", function () {
  function showSection(section) {
    let profile = document.getElementById("profile");
    let create = document.getElementById("create");
    let reset = document.getElementById("reset");

    if (profile) profile.style.display = "none";
    if (create) create.style.display = "none";
    if (reset) reset.style.display = "none";

    let target = document.getElementById(section);
    if (target) target.style.display = "block";
  }

  const profileLink = document.getElementById("profileLink");
  const createLink = document.getElementById("createLink");
  const resetLink = document.getElementById("resetLink");

  if (profileLink) {
    profileLink.addEventListener("click", function () {
      showSection("profile");
    });
  }

  if (createLink) {
    createLink.addEventListener("click", function () {
      showSection("create");
    });
  }

  if (resetLink) {
    resetLink.addEventListener("click", function () {
      showSection("reset");
    });
  }

  if (document.getElementById("profile")) {
    showSection("profile");
  } else if (document.getElementById("create")) {
    showSection("create");
  } else if (document.getElementById("reset")) {
    showSection("reset");
  }
});
