// meter_calculation.js
document.addEventListener("DOMContentLoaded", function () {
  function setupMeterCalc(prefix, type = "super") {
    const fields = {};
    if (type === "super") {
      fields.opening1 = document.getElementById(`${prefix}-super_1_opening`);
      fields.closing1 = document.getElementById(`${prefix}-super_1_closing`);
      fields.opening2 = document.getElementById(`${prefix}-super_2_opening`);
      fields.closing2 = document.getElementById(`${prefix}-super_2_closing`);
      fields.gsaTestDraw = document.getElementById(`${prefix}-gsa_test_draw`);
    } else {
      fields.opening1 = document.getElementById(`${prefix}-d1_opening`);
      fields.closing1 = document.getElementById(`${prefix}-d1_closing`);
      fields.opening2 = document.getElementById(`${prefix}-d2_opening`);
      fields.closing2 = document.getElementById(`${prefix}-d2_closing`);
      fields.opening3 = document.getElementById(`${prefix}-d3_opening`);
      fields.closing3 = document.getElementById(`${prefix}-d3_closing`);
      fields.opening4 = document.getElementById(`${prefix}-d4_opening`);
      fields.closing4 = document.getElementById(`${prefix}-d4_closing`);
      fields.rttLiters = document.getElementById(`${prefix}-rtt_liters`);
    }

    const price = document.getElementById(`${prefix}-price`);
    const litersSoldField = document.getElementById(`${prefix}-liters_sold`);
    const totalField = document.getElementById(`${prefix}-total`);

    if (!price || !litersSoldField || !totalField) return;

    function calcTotals() {
      let litersSold = 0;

      if (type === "super") {
        const s1 =
          (parseFloat(fields.closing1?.value) || 0) -
          (parseFloat(fields.opening1?.value) || 0);
        const s2 =
          (parseFloat(fields.closing2?.value) || 0) -
          (parseFloat(fields.opening2?.value) || 0);
        const gsa = parseFloat(fields.gsaTestDraw?.value) || 0;
        litersSold = s1 + s2 - gsa;
      } else {
        const d1 =
          (parseFloat(fields.closing1?.value) || 0) -
          (parseFloat(fields.opening1?.value) || 0);
        const d2 =
          (parseFloat(fields.closing2?.value) || 0) -
          (parseFloat(fields.opening2?.value) || 0);
        const d3 =
          (parseFloat(fields.closing3?.value) || 0) -
          (parseFloat(fields.opening3?.value) || 0);
        const d4 =
          (parseFloat(fields.closing4?.value) || 0) -
          (parseFloat(fields.opening4?.value) || 0);
        const rtt = parseFloat(fields.rttLiters?.value) || 0;
        litersSold = d1 + d2 + d3 + d4 - rtt;
      }

      const priceVal = parseFloat(price.value) || 0;
      litersSoldField.value = litersSold.toFixed(2);
      totalField.value = (litersSold * priceVal).toFixed(2);
    }

    Object.values(fields).forEach((field) => {
      if (field) field.addEventListener("input", calcTotals);
    });
    price.addEventListener("input", calcTotals);
  }

  setupMeterCalc("s1s2", "super");
  setupMeterCalc("s3s4", "super");
  setupMeterCalc("d1d4", "diesel");
});

// Event listener for the form submission validation
document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");
  const s1Open = document.getElementById("super_1_opening");
  const s1Close = document.getElementById("super_1_closing");
  const s2Open = document.getElementById("super_2_opening");
  const s2Close = document.getElementById("super_2_closing");

  // ✅ Exit silently if form or fields don't exist
  if (!form || !s1Open || !s1Close || !s2Open || !s2Close) return;

  form.addEventListener("submit", function (e) {
    let error = null; // ✅ only one error at a time

    // --- Validation rules ---
    if (parseFloat(s1Close.value) < parseFloat(s1Open.value)) {
      error = "S1 closing must be greater than opening.";
    } else if (parseFloat(s2Close.value) < parseFloat(s2Open.value)) {
      error = "S2 closing must be greater than opening.";
    } else if (s1Close.value.length < s1Open.value.length) {
      error = "S1 closing figure looks incomplete.";
    } else if (s2Close.value.length < s2Open.value.length) {
      error = "S2 closing figure looks incomplete.";
    }

    // --- Stop + Show alert if any error ---
    if (error) {
      e.preventDefault();
      alert(error); // ✅ only ONE message shown
    }
  });
});
// End of form submission validation

// ========== A ===========
// Event listener for electronic and credit totals calculation
document.addEventListener("DOMContentLoaded", function () {
  const creditFields = [
    "gcb",
    "momo",
    "tingg",
    "zenith",
    "credit_ab",
    "credit_cf",
    "credit_gc",
    "credit_wl",
    "credit_zl",
    "soc_staff_credit",

    "republic",
    "prudential",
    "adb",
    "stanbic",
    "ecobank",
    "fidelity",

    "water_bill",
    "ecg_bill",
    "genset",
    "approve_miscellaneous",
  ];
  const collectionFields = [
    "collection_ab",
    "collection_wl",
    "collection_zl",
    "collection_gc",
    "collection_cv",
    "lube_1_liter",
    "lube_drum",
    "duster_collection",
  ];

  const totalCreditField = document.getElementById("total_credit");
  const totalCollectionField = document.getElementById("total_collection");
  const grandTotalField = document.getElementById("grand_total");
  const cashToBankField = document.getElementById("cash_to_bank");

  // ✅ Exit silently if totals fields don’t exist
  if (
    !totalCreditField ||
    !totalCollectionField ||
    !grandTotalField ||
    !cashToBankField
  )
    return;

  let meterTotal = 0;

  // Helper: get current selected section
  function getSelectedSection() {
    const sel = document.getElementById("section");
    return sel ? sel.value : "S1S2";
  }

  // Fetch meter total from backend (with section param)
  function fetchMeterTotal() {
    fetch(
      `/get_meter_total?section=${encodeURIComponent(getSelectedSection())}`
    )
      .then((res) => res.json())
      .then((data) => {
        meterTotal = parseFloat(data.meter_total) || 0;
        calcTotals(); // recalc on load with fetched value
      })
      .catch(() => {
        // ✅ fail silently if fetch fails
      });
  }

  function calcTotals() {
    const sumFields = (ids) =>
      ids.reduce((sum, id) => {
        const el = document.getElementById(id);
        return sum + (parseFloat(el?.value) || 0);
      }, 0);

    const totalCredit = sumFields(creditFields);
    const totalCollection = sumFields(collectionFields);
    const cashToBank = meterTotal - totalCredit + totalCollection;
    const grandTotal = totalCredit + totalCollection + cashToBank;

    totalCreditField.value = totalCredit.toFixed(2);
    totalCollectionField.value = totalCollection.toFixed(2);
    // cashToBankField.value = cashToBank.toFixed(2);
    // grandTotalField.value = grandTotal.toFixed(2);
    cashToBankField.value = Math.round(cashToBank).toFixed(2);
    grandTotalField.value = Math.round(grandTotal).toFixed(2);
  }

  [...creditFields, ...collectionFields].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("input", calcTotals);
  });

  // 🔹 Initial fetch
  fetchMeterTotal();

  // 🔹 Re-fetch if section changes
  document.getElementById("section")?.addEventListener("change", () => {
    fetchMeterTotal();
  });
});
// End of electronic and credit totals calculation

// ========== B ================
// Event listener for the physical cash calculation
document.addEventListener("DOMContentLoaded", () => {
  // ✅ Silent exit if critical fields are missing
  if (
    !document.getElementById("total_credit") &&
    !document.getElementById("total_collection") &&
    !document.getElementById("grand_total") &&
    !document.getElementById("cash_to_bank")
  ) {
    return; // nothing to do on this page
  }

  const creditFields = [
    "gcb",
    "momo",
    "tingg",
    "zenith",
    "credit_ab",
    "credit_cf",
    "credit_gc",
    "credit_wl",
    "credit_zl",
    "soc_staff_credit",
    "republic",
    "prudential",
    "adb",
    "stanbic",
    "ecobank",
    "fidelity",
    "water_bill",
    "ecg_bill",
    "genset",
    "approve_miscellaneous",
  ];

  const collectionFields = [
    "collection_ab",
    "collection_wl",
    "collection_zl",
    "collection_gc",
    "collection_cv",
    "lube_1_liter",
    "lube_drum",
    "duster_collection",
  ];

  const els = {
    totalCredit: document.getElementById("total_credit"),
    totalCollection: document.getElementById("total_collection"),
    grandTotal: document.getElementById("grand_total"),
    cashToBank: document.getElementById("cash_to_bank"),
  };

  let meterTotal = 0;

  // Helper: get current section
  function getSelectedSection() {
    const sel = document.getElementById("section");
    return sel ? sel.value : "S1S2";
  }

  // 🔹 Fetch meter total from backend (with section param)
  function fetchMeterTotal() {
    fetch(
      `/get_meter_total?section=${encodeURIComponent(getSelectedSection())}`
    )
      .then((res) => res.json())
      .then((data) => {
        meterTotal = parseFloat(data.meter_total) || 0;
        calcTotals();
      })
      .catch(() => {}); // silent fail
  }

  function sumFields(ids) {
    return ids.reduce((sum, id) => {
      const val = parseFloat(document.getElementById(id)?.value) || 0;
      return sum + val;
    }, 0);
  }

  function calcTotals() {
    const totalCredit = sumFields(creditFields);
    const totalCollection = sumFields(collectionFields);

    const expectedCashToBank = meterTotal - totalCredit + totalCollection;
    const grandTotal = totalCredit + totalCollection + expectedCashToBank;

    if (els.totalCredit) els.totalCredit.value = totalCredit.toFixed(2);
    if (els.totalCollection)
      els.totalCollection.value = totalCollection.toFixed(2);
    if (els.grandTotal) els.grandTotal.value = grandTotal.toFixed(2);
  }

  [...creditFields, ...collectionFields].forEach((id) => {
    const field = document.getElementById(id);
    if (field) field.addEventListener("input", calcTotals);
  });

  const els2 = {
    totalPhysical: document.getElementById("total_physical_cash"),
    status: document.getElementById("cash_balance_status"),
    paperTotal: document.getElementById("paper_total"),
    coinTotal: document.getElementById("coin_total"),
  };

  let expectedCashToBank = 0;

  // 🔹 Fetch cash_to_bank from backend (with section param)
  function fetchCashToBank() {
    fetch(
      `/get_cash_to_bank?section=${encodeURIComponent(getSelectedSection())}`
    )
      .then((res) => res.json())
      .then((data) => {
        expectedCashToBank = parseFloat(data.cash_to_bank) || 0;
      })
      .catch(() => {}); // silent fail
  }

  // Separate paper vs coins based on field name instead of denom value
  function calcPhysicalCash() {
    let paperTotal = 0;
    let coinTotal = 0;

    // Paper denominations
    document.querySelectorAll("input[id^='note_']").forEach((el) => {
      const denom = parseFloat(el.getAttribute("data-denom")) || 0;
      const qty = parseInt(el.value) || 0;
      paperTotal += denom * qty;
    });

    // Coin denominations
    document.querySelectorAll("input[id^='coin_']").forEach((el) => {
      const denom = parseFloat(el.getAttribute("data-denom")) || 0;
      const qty = parseInt(el.value) || 0;
      coinTotal += denom * qty;
    });

    const totalPhysical = paperTotal + coinTotal;

    if (els2.paperTotal) els2.paperTotal.value = paperTotal.toFixed(2);
    if (els2.coinTotal) els2.coinTotal.value = coinTotal.toFixed(2);
    if (els2.totalPhysical) els2.totalPhysical.value = totalPhysical.toFixed(2);
    if (els.cashToBank) els.cashToBank.value = totalPhysical.toFixed(2);

    if (expectedCashToBank > 0 && els2.status) {
      const roundedPhysical = Math.round(totalPhysical);
      const roundedExpected = Math.round(expectedCashToBank);
      const diff = roundedPhysical - roundedExpected;

      // Reset colors before applying
      els2.status.style.backgroundColor = "";
      if (els2.totalPhysical) els2.totalPhysical.style.backgroundColor = "";

      if (roundedPhysical === roundedExpected) {
        els2.status.value = "✅ Cash Balanced!";
        els2.status.style.color = "green";
        els2.status.style.backgroundColor = "#d4edda"; // light green
        if (els2.totalPhysical)
          els2.totalPhysical.style.backgroundColor = "#d4edda";
      } else if (roundedPhysical < roundedExpected) {
        els2.status.value = `❌ Shortage (Diff: ${diff})`;
        els2.status.style.color = "red";
        els2.status.style.backgroundColor = "#f8d7da"; // light red
        if (els2.totalPhysical)
          els2.totalPhysical.style.backgroundColor = "#f8d7da";
      } else if (roundedPhysical > roundedExpected) {
        els2.status.value = `⚠️ Excess (Diff: +${diff})`;
        els2.status.style.color = "orange";
        els2.status.style.backgroundColor = "#fff3cd"; // light orange
        if (els2.totalPhysical)
          els2.totalPhysical.style.backgroundColor = "#fff3cd";
      }
    }
  }

  document
    .querySelectorAll("input[data-denom]")
    .forEach((el) => el.addEventListener("input", calcPhysicalCash));

  // 🔹 Initial fetches
  fetchMeterTotal();
  fetchCashToBank();

  // 🔹 Re-fetch when section changes
  document.getElementById("section")?.addEventListener("change", () => {
    fetchMeterTotal();
    fetchCashToBank();
  });
});
// End of physical cash calculation

// ✅ Keep hidden field synced with dropdown
document.getElementById("section")?.addEventListener("change", (e) => {
  const hidden = document.querySelector('input[name="selected_section"]');
  if (hidden) hidden.value = e.target.value;
});
// End of hidden field sync
