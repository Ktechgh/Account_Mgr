document.addEventListener("DOMContentLoaded", function () {
  const steps = document.querySelectorAll(".step");
  const progressItems = document.querySelectorAll(".progressbar li");
  const sectionField = document.querySelector("input[name='section']");

  // ✅ Map step forms to their submit buttons
  const submitButtons = {
    step1: document.getElementById("submit_s1s2"), // Flask-WTF submit in Step 1
    step2: document.getElementById("submit_s3s4"),
    step3: document.getElementById("submit_d1d4"),
    step4: document.getElementById("submit_stock"),
  };

  // === Update section based on active step ===
  function updateSection(stepId) {
    if (!sectionField) return;
    switch (stepId) {
      case "step1":
        sectionField.value = "S1S2";
        break;
      case "step2":
        sectionField.value = "S3S4";
        break;
      case "step3":
        sectionField.value = "D1D4";
        break;
      case "step4":
        sectionField.value = "STOCK";
        break;
    }
    console.log("Section updated:", sectionField.value);
  }

  // === Show Step & handle progress/submit buttons ===
  function showStep(stepId) {
    // Hide all steps
    steps.forEach((s) => s.classList.remove("active"));
    const currentStep = document.getElementById(stepId);
    if (currentStep) currentStep.classList.add("active");

    // Progressbar active state
    progressItems.forEach((li, index) => {
      li.classList.remove("active");
      if (li.dataset.step === stepId) {
        li.classList.add("active");
        for (let i = 0; i < index; i++) {
          progressItems[i].classList.add("active");
        }
      }
    });

    // Toggle footer submit buttons
    Object.values(submitButtons).forEach((btn) => {
      if (btn) btn.classList.add("d-none");
    });
    if (submitButtons[stepId]) {
      submitButtons[stepId].classList.remove("d-none");
    }

    // ✅ Update section hidden field
    updateSection(stepId);
  }

  // Next button
  document.querySelectorAll(".next").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const next = btn.getAttribute("data-next");
      if (next) showStep(next);
    });
  });

  // Prev button
  document.querySelectorAll(".prev").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const prev = btn.getAttribute("data-prev");
      if (prev) showStep(prev);
    });
  });

  // Progress bar click
  progressItems.forEach((li) => {
    li.addEventListener("click", () => {
      const stepId = li.dataset.step;
      showStep(stepId);
    });
  });

  // ✅ Set correct section on initial load
  const initialStep = document.querySelector(".step.active");
  if (initialStep) updateSection(initialStep.id);
});
