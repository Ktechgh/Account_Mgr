document.addEventListener("DOMContentLoaded", function () {
  var confirmDeleteModal = document.getElementById("confirmDeleteModal");
  var confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
  var deleteModalMessage = document.getElementById("deleteModalMessage");

  if (confirmDeleteModal) {
    confirmDeleteModal.addEventListener("show.bs.modal", function (event) {
      var button = event.relatedTarget; // Button that triggered the modal
      var deleteUrl = button.getAttribute("data-delete-url");
      var attendantName = button.getAttribute("data-attendant-name");

      // Update modal text
      if (deleteModalMessage) {
        deleteModalMessage.textContent =
          "Are you sure you want to delete " + attendantName + "?";
      }

      // Update delete link
      if (confirmDeleteBtn) {
        confirmDeleteBtn.setAttribute("href", deleteUrl);
      }
    });
  }
});

// For deleting meter readings
document.addEventListener("DOMContentLoaded", function () {
  var confirmDeleteModal = document.getElementById("confirmDeleteModal");
  var confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
  var deleteModalMessage = document.getElementById("deleteModalMessage");

  if (confirmDeleteModal) {
    confirmDeleteModal.addEventListener("show.bs.modal", function (event) {
      var button = event.relatedTarget;
      var deleteUrl = button.getAttribute("data-delete-url");
      var readingId = button.getAttribute("data-reading-id");

      // Update modal text
      if (deleteModalMessage) {
        deleteModalMessage.textContent =
          "Are you sure you want to delete meter reading #" + readingId + "?";
      }

      // Update delete link
      if (confirmDeleteBtn) {
        confirmDeleteBtn.setAttribute("href", deleteUrl);
      }
    });
  }
});

// For deleting meter readings and showing reading ID in modal
document.addEventListener("DOMContentLoaded", function () {
  const deleteButtons = document.querySelectorAll(".delete-btn");
  const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
  const deleteModalMessage = document.getElementById("deleteModalMessage");

  deleteButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const deleteUrl = this.getAttribute("data-delete-url");
      const readingId = this.getAttribute("data-reading-id");

      confirmDeleteBtn.setAttribute("href", deleteUrl);
      deleteModalMessage.textContent = `Are you sure you want to delete record #${readingId} and its entire session?`;
    });
  });
});
