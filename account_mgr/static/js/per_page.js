document.addEventListener("DOMContentLoaded", function () {
  const perPageSelect = document.getElementById("per_page");

  if (perPageSelect) {
    perPageSelect.addEventListener("change", function () {
      this.form.submit();
    });
  }
});
