// // Modal trigger via your PLUS button
// const modalEl = document.getElementById("stepperModal");
// const modal = new bootstrap.Modal(modalEl);
// document.getElementById("openModalBtn_s1s2").onclick = () => modal.show();

// // Stepper logic
// const steps = document.querySelectorAll(".step");
// const progressItems = document.querySelectorAll(".progressbar li");

// document.querySelectorAll(".next").forEach((btn) => {
//   btn.addEventListener("click", (e) => {
//     e.preventDefault();
//     const currentStep = btn.closest(".step");
//     const nextStepId = btn.dataset.next;
//     const nextStep = document.getElementById(nextStepId);
//     if (nextStep) {
//       currentStep.classList.remove("active");
//       nextStep.classList.add("active");
//       const index = Array.from(steps).indexOf(nextStep);
//       progressItems.forEach((li, i) => {
//         li.classList.toggle("active", i <= index);
//       });
//     }
//   });
// });

// document.querySelectorAll(".prev").forEach((btn) => {
//   btn.addEventListener("click", (e) => {
//     e.preventDefault();
//     const currentStep = btn.closest(".step");
//     const prevStepId = btn.dataset.prev;
//     const prevStep = document.getElementById(prevStepId);
//     if (prevStep) {
//       currentStep.classList.remove("active");
//       prevStep.classList.add("active");
//       const index = Array.from(steps).indexOf(prevStep);
//       progressItems.forEach((li, i) => {
//         li.classList.toggle("active", i <= index);
//       });
//     }
//   });
// });



// Modal trigger (keep this part) this is working fine
// const modalEl = document.getElementById("stepperModal");
// const modal = new bootstrap.Modal(modalEl);
// document.getElementById("openModalBtn_s1s2").onclick = () => modal.show();

// // Stepper logic (use B version)
// document.addEventListener("DOMContentLoaded", function () {
//   const steps = document.querySelectorAll(".step");
//   const progressItems = document.querySelectorAll(".progressbar li");

//   function showStep(stepId) {
//     steps.forEach((s) => s.classList.remove("active"));
//     document.getElementById(stepId).classList.add("active");

//     progressItems.forEach((li, index) => {
//       li.classList.remove("active");
//       if (li.dataset.step === stepId) {
//         li.classList.add("active");
//         for (let i = 0; i < index; i++) {
//           progressItems[i].classList.add("active");
//         }
//       }
//     });
//   }

//   document.querySelectorAll(".next").forEach((btn) => {
//     btn.addEventListener("click", () => {
//       const next = btn.getAttribute("data-next");
//       if (next) showStep(next);
//     });
//   });

//   document.querySelectorAll(".prev").forEach((btn) => {
//     btn.addEventListener("click", () => {
//       const prev = btn.getAttribute("data-prev");
//       if (prev) showStep(prev);
//     });
//   });

//   progressItems.forEach((li) => {
//     li.addEventListener("click", () => {
//       const stepId = li.dataset.step;
//       showStep(stepId);
//     });
//   });
// });



document.addEventListener("DOMContentLoaded", () => {
  const modalEl = document.getElementById("stepperModal");
  if (modalEl) {
    const modal = new bootstrap.Modal(modalEl);

    const openBtn = document.getElementById("openModalBtn_s1s2");
    if (openBtn) {
      openBtn.onclick = () => modal.show();
    }
  }

  // Stepper logic (use B version)
  const steps = document.querySelectorAll(".step");
  const progressItems = document.querySelectorAll(".progressbar li");

  function showStep(stepId) {
    steps.forEach((s) => s.classList.remove("active"));
    document.getElementById(stepId)?.classList.add("active");

    progressItems.forEach((li, index) => {
      li.classList.remove("active");
      if (li.dataset.step === stepId) {
        li.classList.add("active");
        for (let i = 0; i < index; i++) {
          progressItems[i].classList.add("active");
        }
      }
    });
  }

  document.querySelectorAll(".next").forEach((btn) => {
    btn.addEventListener("click", () => {
      const next = btn.getAttribute("data-next");
      if (next) showStep(next);
    });
  });

  document.querySelectorAll(".prev").forEach((btn) => {
    btn.addEventListener("click", () => {
      const prev = btn.getAttribute("data-prev");
      if (prev) showStep(prev);
    });
  });

  progressItems.forEach((li) => {
    li.addEventListener("click", () => {
      const stepId = li.dataset.step;
      showStep(stepId);
    });
  });
});
