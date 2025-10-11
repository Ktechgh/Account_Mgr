from account_mgr import db
from sqlalchemy import func
from datetime import datetime, date
from flask_login import login_required
from flask import jsonify, request, Blueprint
from account_mgr.database.models import (
    D14Reading,
    MeterReading,
    ClosingSession,
    CreditTransaction,
)


meter_cash_api = Blueprint(
    import_name=__name__,
    name="meter_cash_api",
    template_folder="templates",
    static_folder="static",
)


@meter_cash_api.route(rule="/get_meter_total")
@login_required
def get_meter_total():
    section = request.args.get(key="section", default="S1S2")

    closing_session = (
        ClosingSession.query.filter_by(section=section, session_date=date.today())
        .order_by(ClosingSession.id.desc())
        .first()
    )

    if not closing_session:
        return jsonify({"meter_total": 0})

    if section.upper() == "D1D4":
        meter_total = (
            db.session.query(D14Reading.total)
            .filter_by(session_id=closing_session.id)
            .order_by(D14Reading.id.desc())
            .first()
        )
    else:
        meter_total = (
            db.session.query(MeterReading.total)
            .filter_by(session_id=closing_session.id)
            .order_by(MeterReading.id.desc())
            .first()
        )

    meter_total_value = float(meter_total[0]) if meter_total and meter_total[0] else 0
    return jsonify({"meter_total": meter_total_value})


@meter_cash_api.route(rule="/get_cash_to_bank")
@login_required
def get_cash_to_bank():
    section = request.args.get(key="section", default="S1S2")

    closing_session = (
        ClosingSession.query.filter_by(section=section, session_date=date.today())
        .order_by(ClosingSession.id.desc())
        .first()
    )

    if not closing_session:
        return jsonify({"cash_to_bank": 0})

    latest_transaction = (
        CreditTransaction.query.filter_by(session_id=closing_session.id)
        .order_by(CreditTransaction.id.desc())
        .first()
    )

    if latest_transaction and latest_transaction.cash_to_bank is not None:
        cash_to_bank_value = float(latest_transaction.cash_to_bank)
    else:
        if section.upper() == "D1D4":
            meter_total = (
                db.session.query(D14Reading.total)
                .filter_by(session_id=closing_session.id)
                .order_by(D14Reading.id.desc())
                .first()
            )
        else:
            meter_total = (
                db.session.query(MeterReading.total)
                .filter_by(session_id=closing_session.id)
                .order_by(MeterReading.id.desc())
                .first()
            )
        cash_to_bank_value = (
            float(meter_total[0]) if meter_total and meter_total[0] else 0
        )

    return jsonify({"cash_to_bank": cash_to_bank_value})


@meter_cash_api.route(rule="/get_meter_reading")
@login_required
def get_meter_reading():
    date_str = request.args.get(key="date")
    section = request.args.get(key="section")

    if not date_str:
        return jsonify({"success": False, "message": "No date provided."})
    if not section:
        return jsonify({"success": False, "message": "No section provided."})

    try:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"success": False, "message": "Invalid date format."})

    if section.upper() == "D1D4":
        reading = D14Reading.query.filter(
            func.lower(D14Reading.section) == section.lower(),
            D14Reading.date_of_sale == selected_date,
        ).first()

        if not reading:
            return jsonify(
                {
                    "success": False,
                    "message": f"No record found for {section} on {selected_date}",
                }
            )

        return jsonify(
            {
                "success": True,
                "d1_opening": float(reading.d1_closing or 0),
                "d2_opening": float(reading.d2_closing or 0),
                "d3_opening": float(reading.d3_closing or 0),
                "d4_opening": float(reading.d4_closing or 0),
            }
        )
    else:
        reading = MeterReading.query.filter(
            func.lower(MeterReading.section) == section.lower(),
            MeterReading.date_of_sale == selected_date,
        ).first()

        if not reading:
            return jsonify(
                {
                    "success": False,
                    "message": f"No record found for {section} on {selected_date}",
                }
            )

        return jsonify(
            {
                "success": True,
                "super_1_opening": float(reading.super_1_closing or 0),
                "super_2_opening": float(reading.super_2_closing or 0),
            }
        )
