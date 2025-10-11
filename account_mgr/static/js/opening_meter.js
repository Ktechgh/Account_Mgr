// opening_meter.js
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("button[id^='fetchMeterBtn']").forEach((btn) => {
    btn.addEventListener("click", function () {
      const form = btn.closest("form");
      const dateInput = form.querySelector("input[id^='date_of_sale']");

      if (!dateInput || !dateInput.value) {
        alert("Please select a date first.");
        return;
      }

      const openingField =
        form.querySelector("[id$='-super_1_opening']") ||
        form.querySelector("[id$='-d1_opening']"); // support diesel
      if (!openingField) {
        alert("Could not detect form prefix. Check field IDs.");
        return;
      }

      const prefix = openingField.id.split("-")[0]; // s1s2, s3s4, d1d4
      const section = prefix.toUpperCase();

      fetch(`/get_meter_reading?date=${dateInput.value}&section=${section}`)
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            if (section === "D1D4") {
              form.querySelector(`#${prefix}-d1_opening`).value =
                data.d1_opening;
              form.querySelector(`#${prefix}-d2_opening`).value =
                data.d2_opening;
              form.querySelector(`#${prefix}-d3_opening`).value =
                data.d3_opening;
              form.querySelector(`#${prefix}-d4_opening`).value =
                data.d4_opening;
            } else {
              form.querySelector(`#${prefix}-super_1_opening`).value =
                data.super_1_opening;
              form.querySelector(`#${prefix}-super_2_opening`).value =
                data.super_2_opening;
            }
          } else {
            alert(
              data.message || `No meter data found for ${section} on that date.`
            );
          }
        })
        .catch((err) => {
          console.error("Error fetching meter data:", err);
          alert("Error fetching meter data.");
        });
    });
  });
});
