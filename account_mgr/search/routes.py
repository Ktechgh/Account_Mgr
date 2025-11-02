import io
import pandas as pd
from enum import Enum
from sqlalchemy import or_
from account_mgr import db
from flask import send_file
from num2words import num2words
from .message import message_map
from datetime import datetime, time
from flask_login import login_required
from datetime import datetime, time, date
from flask import redirect, url_for, flash
from flask import render_template, Blueprint, flash, request
from account_mgr.super_admin.routes import super_admin_required
from .form import TransactionReportForm, PerPageForm, CashSummaryForm
from account_mgr.database.models import (
    D14Reading,
    MeterReading,
    ClosingSession,
    CreditTransaction,
    CoinsTransaction,
    PaperTransaction,
)


transactions_bp = Blueprint(
    "transactions_bp", __name__, template_folder="templates", static_folder="static"
)


# ---------------- REPORT TYPES -----------------
class ReportType(Enum):
    METER_READING = "Meter Reading"
    D14_READING = "D1-D4 Diesel Reading"
    CREDIT = "Credit Transaction"
    PAPER = "Paper Transaction"
    COINS = "Coins Transaction"
    CLOSING_SESSION = "Closing Session"
    ALL = "All"


# lowercase -> ReportType.value
REPORT_TYPE_MAP = {
    "all": ReportType.ALL.value,
    "meter": ReportType.METER_READING.value,
    "d14": ReportType.D14_READING.value,
    "credit": ReportType.CREDIT.value,
    "paper": ReportType.PAPER.value,
    "coins": ReportType.COINS.value,
    "closing": ReportType.CLOSING_SESSION.value,
}


def generate_report(report_type, start_date, end_date):
    start_datetime = datetime.combine(start_date, time.min)
    end_datetime = datetime.combine(end_date, time.max)

    mapping = {
        ReportType.METER_READING.value: (MeterReading, MeterReading.date_of_sale),
        ReportType.D14_READING.value: (D14Reading, D14Reading.date_of_sale),
        ReportType.CREDIT.value: (CreditTransaction, CreditTransaction.date_created),
        ReportType.PAPER.value: (PaperTransaction, PaperTransaction.date_created),
        ReportType.COINS.value: (CoinsTransaction, CoinsTransaction.date_created),
        ReportType.CLOSING_SESSION.value: (ClosingSession, ClosingSession.date_created),
    }

    if report_type == ReportType.ALL.value:
        result_dict = {}
        for key, (model, field) in mapping.items():
            result_dict[key] = model.query.filter(
                field.between(start_datetime, end_datetime)
            ).all()
        return result_dict
    else:
        model_field = mapping.get(report_type)
        if not model_field:
            return None

        model, field = model_field
        return model.query.filter(field.between(start_datetime, end_datetime)).all()


# ---------------- ROUTE -----------------
@transactions_bp.route(rule="/account_mgr/transaction/report", methods=["GET", "POST"])
@login_required
@super_admin_required
def transaction_report():
    form = TransactionReportForm()
    per_page_form = PerPageForm()
    results = []
    report_type = None
    report_title = "Station Report"

    if form.validate_on_submit():
        # Normalize lowercase form value to ReportType value
        report_type = REPORT_TYPE_MAP.get(form.report_type.data)
        if report_type:
            results = generate_report(
                report_type, form.start_date.data, form.end_date.data
            )

    if results is None:
        flash(message=message_map["error_invalid_choice"], category="error")
    elif results:
        if isinstance(results, dict):  # ALL
            count = sum(len(v) for v in results.values())
            if count > 0:
                flash(
                    message=f"{message_map['success']} {count} items found.",
                    category="success",
                )
            else:
                flash(message=message_map["error"], category="error")
                results = []
        else:  # single model list
            count = len(results)
            if count > 0:
                flash(
                    message=f"{message_map['success']} {count} items found.",
                    category="success",
                )
            else:
                flash(message=message_map["error"], category="error")
                results = []
    else:
        flash(message=message_map["error"], category="error")

    # Pagination (example for meter readings)
    page = request.args.get(key="page", default=1, type=int)
    per_page = request.args.get(key="per_page", default=5, type=int)
    per_page_form.per_page.data = per_page

    meter_readings = MeterReading.query.order_by(
        MeterReading.date_of_sale.desc()
    ).paginate(page=page, per_page=per_page)

    return render_template(
        "transaction_result.html",
        form=form,
        results=results,
        ReportType=ReportType,
        meter_readings=meter_readings,
        report_type=report_type,
        report_title=report_title,
        per_page_form=per_page_form,
    )


@transactions_bp.route(rule="/account_mgr/transaction/export", methods=["GET"])
@login_required
@super_admin_required
def export_transaction_report():
    # read query params
    start_date_str = request.args.get(key="start_date")
    end_date_str = request.args.get(key="end_date")
    report_type = request.args.get(key="report_type", default="all")

    try:
        start_date = (
            datetime.strptime(start_date_str, "%Y-%m-%d").date()
            if start_date_str
            else date.today()
        )
        end_date = (
            datetime.strptime(end_date_str, "%Y-%m-%d").date()
            if end_date_str
            else date.today()
        )
    except Exception:
        flash(message="Invalid date format. Use YYYY-MM-DD.", category="error")
        return redirect(url_for(endpoint="transactions_bp.transaction_report"))

    # get results
    report_type_value = REPORT_TYPE_MAP.get(report_type.lower(), ReportType.ALL.value)
    results = generate_report(report_type_value, start_date, end_date)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:

        def export_df(sheet_name, rows, columns, row_mapper):
            """Helper to export consistent DataFrame with formatting."""
            df = pd.DataFrame([row_mapper(r) for r in rows], columns=columns)
            df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Apply formatting
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]

            # Header format
            header_format = workbook.add_format(
                {
                    "bold": True,
                    "text_wrap": True,
                    "valign": "vcenter",
                    "align": "center",
                    "bg_color": "#D9E1F2",  # light blue shade
                    "border": 1,
                }
            )

            # Format headers
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)

            # Auto-adjust column widths
            for i, col in enumerate(df.columns):
                col_width = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, col_width)

            # Freeze the first row
            worksheet.freeze_panes(1, 0)

        # ---------- MAPPINGS ----------
        def closing_session_mapper(r):
            return [
                r.id,
                r.section,
                r.admin_user_name or "N/A",
                r.date_created.strftime("%d-%m-%Y %I:%M %p"),
            ]

        closing_session_cols = ["ID", "Section", "Admin Username", "Date Created"]

        def meter_reading_mapper(r):
            return [
                r.id,
                getattr(r.session, "section", "N/A"),
                r.super_1_opening,
                r.super_2_opening,
                r.super_1_closing,
                r.super_2_closing,
                r.liters_sold,
                r.gsa_test_draw or "N/A",
                r.price,
                r.total,
                r.csa_name,
                r.date_of_sale.strftime("%d-%m-%Y"),
                r.date_created.strftime("%d-%m-%Y %I:%M %p"),
            ]

        meter_reading_cols = [
            "ID",
            "Section",
            "Super 1 Opening",
            "Super 2 Opening",
            "Super 1 Closing",
            "Super 2 Closing",
            "Sale Liter",
            "RTT",
            "Price",
            "Total",
            "CSA Name",
            "Date of Sale",
            "Date Created",
        ]

        def d14_mapper(r):
            return [
                r.id,
                getattr(r.session, "section", "N/A"),
                # r.section,
                r.d1_opening,
                r.d1_closing,
                r.d2_opening,
                r.d2_closing,
                r.d3_opening,
                r.d3_closing,
                r.d4_opening,
                r.d4_closing,
                r.rtt_liters or "N/A",
                r.liters_sold,
                r.price,
                r.total,
                r.csa_name,
                r.date_of_sale.strftime("%d-%m-%Y"),
                r.date_created.strftime("%d-%m-%Y %I:%M %p"),
            ]

        d14_cols = [
            "ID",
            "Section",
            "D1 Opening",
            "D1 Closing",
            "D2 Opening",
            "D2 Closing",
            "D3 Opening",
            "D3 Closing",
            "D4 Opening",
            "D4 Closing",
            "RTT",
            "Sale Liter",
            "Price",
            "Total",
            "CSA Name",
            "Date of Sale",
            "Date Created",
        ]

        def credit_mapper(r):
            return [
                r.id,
                getattr(r.session, "section", "N/A"),
                r.gcb,
                r.momo,
                r.tingg,
                r.zenith,
                r.republic,
                r.prudential,
                r.adb,
                r.stanbic,
                r.ecobank,
                r.fidelity,
                r.credit_ab,
                r.credit_cf,
                r.credit_gc,
                r.credit_wl,
                r.soc_staff_credit,
                r.water_bill,
                r.ecg_bill,
                r.genset,
                r.approve_miscellaneous,
                r.collection_ab,
                r.collection_wl,
                r.collection_gc,
                r.collection_cv,
                r.lube_1_liter,
                r.lube_drum,
                r.duster_collection,
                r.total_collection,
                r.total_credit,
                r.cash_to_bank,
                r.grand_total,
                r.date_created.strftime("%d-%m-%Y"),
            ]

        credit_cols = [
            "ID",
            "Section",
            "GCB",
            "MoMo",
            "Tingg",
            "Zenith",
            "Republic",
            "Prudential",
            "ADB",
            "Stanbic",
            "Ecobank",
            "Fidelity",
            "Credit AB",
            "Credit CF",
            "Credit ZM",
            "Credit WL",
            "Soc Staff Credit",
            "Water Bill",
            "ECG Bill",
            "Genset",
            "Approve Misc",
            "Collection AB",
            "Collection WL",
            "Collection GC",
            "Collection CV",
            "Lube (1L)",
            "Lube Drum",
            "Duster Collection",
            "Total Collections",
            "Total Credit/E-Cash",
            "Cash to Bank",
            "Grand Total",
            "Date",
        ]

        def paper_mapper(r):
            return [
                r.id,
                getattr(r.session, "section", "N/A"),
                r.note_200,
                r.note_100,
                r.note_50,
                r.note_20,
                r.note_10,
                r.note_5,
                r.note_2,
                r.note_1,
                r.date_created.strftime("%d-%m-%Y"),
            ]

        paper_cols = [
            "ID",
            "Section",
            "₵200",
            "₵100",
            "₵50",
            "₵20",
            "₵10",
            "₵5",
            "₵2",
            "₵1",
            "Date",
        ]

        def coins_mapper(r):
            return [
                r.id,
                getattr(r.session, "section", "N/A"),
                r.coin_5,
                r.coin_2,
                r.coin_1,
                r.date_created.strftime("%d-%m-%Y"),
            ]

        coins_cols = ["ID", "Section", "₵2 coin", "₵1 coin", "50 ps", "Date"]

        # ---------- EXPORT ----------
        if isinstance(results, dict):  # ALL
            for key, rows in results.items():
                if not rows:
                    continue
                if key == ReportType.CLOSING_SESSION.value:
                    export_df(
                        "Closing_Session",
                        rows,
                        closing_session_cols,
                        closing_session_mapper,
                    )
                elif key == ReportType.METER_READING.value:
                    export_df(
                        "Meter_Reading", rows, meter_reading_cols, meter_reading_mapper
                    )
                elif key == ReportType.D14_READING.value:
                    export_df("Diesel_D1_D4", rows, d14_cols, d14_mapper)
                elif key == ReportType.CREDIT.value:
                    export_df("Credit_Transactions", rows, credit_cols, credit_mapper)
                elif key == ReportType.PAPER.value:
                    export_df("Paper_Cash", rows, paper_cols, paper_mapper)
                elif key == ReportType.COINS.value:
                    export_df("Coins", rows, coins_cols, coins_mapper)
        else:  # single report
            if report_type_value == ReportType.CLOSING_SESSION.value:
                export_df(
                    "Closing_Session",
                    results,
                    closing_session_cols,
                    closing_session_mapper,
                )
            elif report_type_value == ReportType.METER_READING.value:
                export_df(
                    "Meter_Reading", results, meter_reading_cols, meter_reading_mapper
                )
            elif report_type_value == ReportType.D14_READING.value:
                export_df("Diesel_D1_D4", results, d14_cols, d14_mapper)
            elif report_type_value == ReportType.CREDIT.value:
                export_df("Credit_Transactions", results, credit_cols, credit_mapper)
            elif report_type_value == ReportType.PAPER.value:
                export_df("Paper_Cash", results, paper_cols, paper_mapper)
            elif report_type_value == ReportType.COINS.value:
                export_df("Coins", results, coins_cols, coins_mapper)

    output.seek(0)

    if start_date == end_date:
        filename = f"transaction_report_{start_date.strftime('%d-%m-%Y')}.xlsx"
    else:
        filename = f"transaction_report_{start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}.xlsx"

    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def amount_to_words(amount):
    """
    Convert numeric currency amount to proper Ghana Cedis words.
    Handles both whole and decimal parts accurately.
    Example: 46341.25 -> 'Forty-six thousand, three hundred and forty-one Ghana cedis, twenty-five pesewas'
    """
    amount = round(float(amount), 2)
    cedis = int(amount)
    pesewas = int(round((amount - cedis) * 100))

    cedis_words = num2words(cedis, lang="en").replace("-", " ").capitalize()
    if pesewas > 0:
        pesewas_words = num2words(pesewas, lang="en").replace("-", " ")
        return f"{cedis_words} Ghana cedis, {pesewas_words} pesewas"
    else:
        return f"{cedis_words} Ghana cedis only"


@transactions_bp.route(rule="account_mgr/cash_summary", methods=["GET", "POST"])
@login_required
def cash_summary():
    form_cash = CashSummaryForm()
    cash_report_title = "Cash Summary Report"

    def get_totals(
        is_reconciliation=False, start_date=None, end_date=None, report_type="all"
    ):
        """Helper function to compute totals for either normal or reconciled entries."""
        paper_totals = {f"note_{val}": 0 for val in [200, 100, 50, 20, 10, 5, 2, 1]}
        coin_totals = {f"coin_{val}": 0 for val in [5, 2, 1]}

        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)

        # ✅ Use correct filter based on reconciliation
        if is_reconciliation:
            paper_filter = PaperTransaction.is_reconciliation.is_(True)
            coin_filter = CoinsTransaction.is_reconciliation.is_(True)
        else:
            paper_filter = or_(
                PaperTransaction.is_reconciliation.is_(False),
                PaperTransaction.is_reconciliation.is_(None),
            )
            coin_filter = or_(
                CoinsTransaction.is_reconciliation.is_(False),
                CoinsTransaction.is_reconciliation.is_(None),
            )

        # 🔹 Query paper only if user requested "all" or "paper"
        paper_rows = []
        if report_type in ["all", "paper"]:
            paper_rows = PaperTransaction.query.filter(
                paper_filter,
                PaperTransaction.date_created.between(start_datetime, end_datetime),
            ).all()

            for row in paper_rows:
                paper_totals["note_200"] += row.note_200 or 0
                paper_totals["note_100"] += row.note_100 or 0
                paper_totals["note_50"] += row.note_50 or 0
                paper_totals["note_20"] += row.note_20 or 0
                paper_totals["note_10"] += row.note_10 or 0
                paper_totals["note_5"] += row.note_5 or 0
                paper_totals["note_2"] += row.note_2 or 0
                paper_totals["note_1"] += row.note_1 or 0

        # 🔹 Query coins only if user requested "all" or "coins"
        coins_rows = []
        if report_type in ["all", "coins"]:
            coins_rows = CoinsTransaction.query.filter(
                coin_filter,
                CoinsTransaction.date_created.between(start_datetime, end_datetime),
            ).all()

            for row in coins_rows:
                coin_totals["coin_5"] += row.coin_5 or 0
                coin_totals["coin_2"] += row.coin_2 or 0
                coin_totals["coin_1"] += row.coin_1 or 0

        # 🔹 Total value (only include what was selected)
        total_value = 0
        if report_type in ["all", "paper"]:
            total_value += (
                paper_totals["note_200"] * 200
                + paper_totals["note_100"] * 100
                + paper_totals["note_50"] * 50
                + paper_totals["note_20"] * 20
                + paper_totals["note_10"] * 10
                + paper_totals["note_5"] * 5
                + paper_totals["note_2"] * 2
                + paper_totals["note_1"] * 1
            )

        if report_type in ["all", "coins"]:
            total_value += (
                coin_totals["coin_5"] * 0.5
                + coin_totals["coin_2"] * 2
                + coin_totals["coin_1"] * 1
            )

        return paper_totals, coin_totals, total_value

    # Default values
    paper_totals = coin_totals = {}
    rec_paper_totals = rec_coin_totals = {}
    total_value = rec_total_value = 0
    total_s_liters = total_d_liters = combined_liters = 0

    total_value_words = ""
    rec_total_value_words = ""

    if form_cash.validate_on_submit():
        start_date = form_cash.start_date.data
        end_date = form_cash.end_date.data
        report_type = form_cash.cash_report_type.data

        # 🔹 Fetch both normal and reconciled data, using report_type properly
        paper_totals, coin_totals, total_value = get_totals(
            False, start_date, end_date, report_type
        )
        rec_paper_totals, rec_coin_totals, rec_total_value = get_totals(
            True, start_date, end_date, report_type
        )

        # 🔹 Liters summary
        s_rows = MeterReading.query.filter(
            MeterReading.date_created.between(
                datetime.combine(start_date, time.min),
                datetime.combine(end_date, time.max),
            )
        ).all()

        d_rows = D14Reading.query.filter(
            D14Reading.date_created.between(
                datetime.combine(start_date, time.min),
                datetime.combine(end_date, time.max),
            )
        ).all()

        total_s_liters = sum(row.liters_sold for row in s_rows)
        total_d_liters = sum(row.liters_sold for row in d_rows)
        combined_liters = total_s_liters + total_d_liters

        total_value_words = amount_to_words(total_value)
        rec_total_value_words = amount_to_words(rec_total_value)

        flash(message="Cash summary generated successfully!", category="success")

    return render_template(
        "cash_summary.html",
        form_cash=form_cash,
        cash_report_title=cash_report_title,
        paper_totals=paper_totals,
        coin_totals=coin_totals,
        total_value=total_value,
        total_value_words=total_value_words,
        rec_paper_totals=rec_paper_totals,
        rec_coin_totals=rec_coin_totals,
        rec_total_value=rec_total_value,
        rec_total_value_words=rec_total_value_words,
        total_s_liters=total_s_liters,
        total_d_liters=total_d_liters,
        combined_liters=combined_liters,
    )


@transactions_bp.route(rule="account_mgr/cash_summary/export", methods=["GET"])
@login_required
def export_cash_summary():
    # read query params (expected format YYYY-MM-DD from HTML date inputs)
    start_date_str = request.args.get(key="start_date")
    end_date_str = request.args.get(key="end_date")
    report_type = request.args.get(key="cash_report_type", default="all")

    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        else:
            start_date = date.today()
        if end_date_str:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        else:
            end_date = date.today()
    except Exception:
        flash(
            message="Invalid date format for export. Use YYYY-MM-DD.", category="error"
        )
        return redirect(url_for(endpoint="transactions_bp.cash_summary"))

    start_dt = datetime.combine(start_date, time.min)
    end_dt = datetime.combine(end_date, time.max)

    # fetch rows
    paper_rows, coins_rows, s_rows, d_rows = [], [], [], []

    if report_type in ["all", "paper"]:
        paper_rows = PaperTransaction.query.filter(
            PaperTransaction.date_created.between(start_dt, end_dt)
        ).all()

    if report_type in ["all", "coins"]:
        coins_rows = CoinsTransaction.query.filter(
            CoinsTransaction.date_created.between(start_dt, end_dt)
        ).all()

    s_rows = MeterReading.query.filter(
        MeterReading.date_created.between(start_dt, end_dt)
    ).all()
    d_rows = D14Reading.query.filter(
        D14Reading.date_created.between(start_dt, end_dt)
    ).all()

    # 🛑 If no data at all, return empty Excel
    if not (paper_rows or coins_rows or s_rows or d_rows):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter"):
            pass  # don't add any sheets, keep it empty
        output.seek(0)

        if start_date == end_date:
            filename = f"cash_summary_{start_date.strftime('%d-%m-%Y')}.xlsx"
        else:
            filename = f"cash_summary_{start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}.xlsx"

        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    # ✅ If rows exist, continue computing totals
    paper_totals = {f"note_{val}": 0 for val in [200, 100, 50, 20, 10, 5, 2, 1]}
    coin_totals = {f"coin_{val}": 0 for val in [5, 2, 1]}

    for row in paper_rows:
        paper_totals["note_200"] += row.note_200 or 0
        paper_totals["note_100"] += row.note_100 or 0
        paper_totals["note_50"] += row.note_50 or 0
        paper_totals["note_20"] += row.note_20 or 0
        paper_totals["note_10"] += row.note_10 or 0
        paper_totals["note_5"] += row.note_5 or 0
        paper_totals["note_2"] += row.note_2 or 0
        paper_totals["note_1"] += row.note_1 or 0

    for row in coins_rows:
        coin_totals["coin_5"] += row.coin_5 or 0
        coin_totals["coin_2"] += row.coin_2 or 0
        coin_totals["coin_1"] += row.coin_1 or 0

    total_s_liters = sum((row.liters_sold or 0) for row in s_rows)
    total_d_liters = sum((row.liters_sold or 0) for row in d_rows)
    combined_liters = total_s_liters + total_d_liters

    # build DataFrames (same as before)...
    rows = []
    rows.append(
        ("₵200", paper_totals["note_200"], float(paper_totals["note_200"] * 200))
    )
    rows.append(
        ("₵100", paper_totals["note_100"], float(paper_totals["note_100"] * 100))
    )
    rows.append(("₵50", paper_totals["note_50"], float(paper_totals["note_50"] * 50)))
    rows.append(("₵20", paper_totals["note_20"], float(paper_totals["note_20"] * 20)))
    rows.append(("₵10", paper_totals["note_10"], float(paper_totals["note_10"] * 10)))
    rows.append(("₵5", paper_totals["note_5"], float(paper_totals["note_5"] * 5)))
    rows.append(("₵2", paper_totals["note_2"], float(paper_totals["note_2"] * 2)))
    rows.append(("₵1", paper_totals["note_1"], float(paper_totals["note_1"] * 1)))
    rows.append(("₵2 Coin", coin_totals["coin_2"], float(coin_totals["coin_2"] * 2)))
    rows.append(("₵1 Coin", coin_totals["coin_1"], float(coin_totals["coin_1"] * 1)))
    rows.append(
        ("₵0.50 Coin", coin_totals["coin_5"], float(coin_totals["coin_5"] * 0.5))
    )

    df_cash = pd.DataFrame(rows, columns=["Denomination", "Pieces", "Value"])
    df_cash.loc[len(df_cash.index)] = [None, None, None]
    df_cash.loc[len(df_cash.index)] = ["Cash to bank", "", df_cash["Value"].sum()]

    df_liters = pd.DataFrame(
        [
            ["Super (S1 - S4)", float(total_s_liters)],
            ["Diesel (D1 - D4)", float(total_d_liters)],
        ],
        columns=["Category", "Liters Sold"],
    )
    df_liters.loc[len(df_liters.index)] = [None, None]
    df_liters.loc[len(df_liters.index)] = [
        "Total (S1-S4 + D1-D4)",
        float(combined_liters),
    ]

    # write to excel with formatting (same as before)...
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_cash.to_excel(writer, sheet_name="Cash", index=False)
        df_liters.to_excel(writer, sheet_name="Liters", index=False)

        workbook = writer.book
        header_format = workbook.add_format(
            {
                "bold": True,
                "align": "center",
                "valign": "vcenter",
                "bg_color": "#D9E1F2",
                "border": 1,
            }
        )

        sheet_cash = writer.sheets["Cash"]
        for col_num, value in enumerate(df_cash.columns.values):
            sheet_cash.write(0, col_num, value, header_format)
            max_len = max(df_cash[value].astype(str).map(len).max(), len(value)) + 2
            sheet_cash.set_column(col_num, col_num, max_len)
        sheet_cash.freeze_panes(1, 0)

        sheet_liters = writer.sheets["Liters"]
        for col_num, value in enumerate(df_liters.columns.values):
            sheet_liters.write(0, col_num, value, header_format)
            max_len = max(df_liters[value].astype(str).map(len).max(), len(value)) + 2
            sheet_liters.set_column(col_num, col_num, max_len)
        sheet_liters.freeze_panes(1, 0)

    output.seek(0)
    if start_date == end_date:
        filename = f"cash_summary_{start_date.strftime(format='%d-%m-%Y')}.xlsx"
    else:
        filename = f"cash_summary_{start_date.strftime(format='%d-%m-%Y')} to {end_date.strftime(format='%d-%m-%Y')}.xlsx"

    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# ---------------- DELETE METER READING -----------------
@transactions_bp.route(rule="/account_mgr/delete_meter_reading/<int:reading_id>")
@login_required
def delete_meter_reading(reading_id):
    # Get the meter reading
    reading = MeterReading.query.get_or_404(reading_id)

    # Get the whole session that this reading belongs to
    session = reading.session

    try:
        # Delete the entire ClosingSession
        db.session.delete(session)
        db.session.commit()
        flash(
            message="Closing session (and all related data) deleted successfully.",
            category="success",
        )
    except Exception as e:
        db.session.rollback()
        flash(message=f"Error deleting closing session: {str(e)}", category="error")

    return redirect(url_for(endpoint="super_admin_secure.secure_adashboard"))


# ---------------- DELETE D14 READING -----------------
@transactions_bp.route("/account_mgr/delete_d14_reading/<int:reading_id>")
@login_required
def delete_d14_reading(reading_id):
    # Get the diesel (D1-D4) reading
    reading = D14Reading.query.get_or_404(reading_id)

    # Get the ClosingSession that this reading belongs to
    session = reading.session

    try:
        # Delete the entire ClosingSession (cascade deletes all linked data)
        db.session.delete(session)
        db.session.commit()
        flash(
            message="Closing session (and all related data) deleted successfully.",
            category="success",
        )
    except Exception as e:
        db.session.rollback()
        flash(message=f"Error deleting closing session: {str(e)}", category="error")

    # Redirect user back to dashboard
    return redirect(url_for(endpoint="super_admin_secure.secure_adashboard"))
