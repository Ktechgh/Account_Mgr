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

// Cash Summary Modal
document.addEventListener("DOMContentLoaded", function () {
  const cashSummaryModal = document.getElementById("cashSummaryModal");
  const cashSummaryBtn = document.querySelector(".cash-summary-trigger");

  if (!cashSummaryModal || !cashSummaryBtn) return;

  const closeCashSummaryX = cashSummaryModal.querySelector(
    "span.close-cash-summary"
  );

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

// Access Control Modal
document.addEventListener("DOMContentLoaded", function () {
  const accessModal = document.getElementById("accessControlModal");
  const accessBtn = document.querySelector(".access-control-trigger");

  if (!accessModal || !accessBtn) return;

  const closeAccessX = accessModal.querySelector("span.close-access-modal");

  accessBtn.addEventListener("click", function (e) {
    e.preventDefault();
    accessModal.style.display = "block";
  });

  if (closeAccessX) {
    closeAccessX.addEventListener("click", function () {
      accessModal.style.display = "none";
    });
  }

  window.addEventListener("click", function (e) {
    if (e.target === accessModal) {
      accessModal.style.display = "none";
    }
  });
});
// End of Access Control Modal

// Admin PIN Verification
document.addEventListener("DOMContentLoaded", function () {
  let pinInput = document.getElementById("admin_pin");
  let submitBtn = document.getElementById("access-btn");
  let statusMsg = document.getElementById("pin-status");

  submitBtn.disabled = true;

  pinInput.addEventListener("input", function () {
    if (pinInput.value.trim() === "") {
      submitBtn.disabled = true;
      statusMsg.textContent = "";
      return;
    }

    const csrf = document.querySelector('meta[name="csrf--token"]').content;

    fetch("/account_mgr/verify_pin", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: `pin=${pinInput.value}&csrf_token=${csrf}`,
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.valid) {
          statusMsg.textContent = "✅ PIN correct";
          statusMsg.style.color = "green";
          submitBtn.disabled = false;
        } else {
          statusMsg.textContent = "❌ Invalid PIN";
          statusMsg.style.color = "red";
          submitBtn.disabled = true;
        }
      });
  });
});
// End of Admin PIN Verification