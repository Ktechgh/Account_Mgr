// Transaction Report Modal
document.addEventListener("DOMContentLoaded", function () {
  const transReportModal = document.getElementById("transReportModal");
  const transReportBtn = document.querySelector(".trans-report-trigger");

  // Only continue if modal and button exist
  if (!transReportModal || !transReportBtn) return;

  const closeTransReportBtn = transReportModal.querySelector(
    ".close-trans-report"
  );

  transReportBtn.addEventListener("click", function (e) {
    e.preventDefault();
    transReportModal.style.display = "block";
  });

  if (closeTransReportBtn) {
    closeTransReportBtn.addEventListener("click", function () {
      transReportModal.style.display = "none";
    });
  }

  window.addEventListener("click", function (e) {
    if (e.target === transReportModal) {
      transReportModal.style.display = "none";
    }
  });
});
// End of Transaction Report Modal

// // Cash Summary Modal
// document.addEventListener("DOMContentLoaded", function () {
//   const cashSummaryModal = document.getElementById("cashSummaryModal");
//   const cashSummaryBtn = document.querySelector(".cash-summary-trigger");

//   if (!cashSummaryModal || !cashSummaryBtn) return;

//   const closeCashSummaryBtn = cashSummaryModal.querySelector(".close-cash-summary");

//   cashSummaryBtn.addEventListener("click", function (e) {
//     e.preventDefault();
//     cashSummaryModal.style.display = "block";
//   });

//   if (closeCashSummaryBtn) {
//     closeCashSummaryBtn.addEventListener("click", function () {
//       cashSummaryModal.style.display = "none";
//     });
//   }

//   window.addEventListener("click", function (e) {
//     if (e.target === cashSummaryModal) {
//       cashSummaryModal.style.display = "none";
//     }
//   });
// });
// // End of Cash Summary Modal

// Cash Summary Modal
document.addEventListener("DOMContentLoaded", function () {
  const cashSummaryModal = document.getElementById("cashSummaryModal");
  const cashSummaryBtn = document.querySelector(".cash-summary-trigger");

  if (!cashSummaryModal || !cashSummaryBtn) return;

  const closeCashSummaryX = cashSummaryModal.querySelector("span.close-cash-summary");

  cashSummaryBtn.addEventListener("click", function (e) {
    e.preventDefault();
    cashSummaryModal.style.display = "block";
  });

  if (closeCashSummaryX) {
    closeCashSummaryX.addEventListener("click", function () {
      cashSummaryModal.style.display = "none";
    });
  }

  window.addEventListener("click", function (e) {
    if (e.target === cashSummaryModal) {
      cashSummaryModal.style.display = "none";
    }
  });
});
// End of Cash Summary Modal