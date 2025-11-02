from account_mgr import bcrypt, db
from flask_login import current_user
from flask_wtf.csrf import validate_csrf, CSRFError
from .form import AccessControlForm, DailyReportForm
from account_mgr.database.models import ClosingSession, DailyReport
from flask import render_template, Blueprint, redirect, flash, url_for, request


access_control_bp = Blueprint(
    import_name=__name__,
    name="access_control",
    template_folder="templates",
    static_folder="static",
)


# @access_control_bp.route("/account_mgr/access_control", methods=["GET", "POST"])
# def access_control():
#     form = AccessControlForm()

#     if form.validate_on_submit():
#         access_type = form.access.data.lower()
#         start_date = form.start_date.data
#         end_date = form.end_date.data

#         # ✅ Map user UI labels to DB section codes
#         access_map = {
#             "s1-s2": "S1S2",
#             "s3-s4": "S3S4",
#             "d1-d4": "D1D4",
#         }

#         combined_section = access_map.get(access_type)

#         if not combined_section:
#             flash(message="Invalid selection ❌", category="error")
#             return redirect(url_for(endpoint="super_admin_secure.secure_adashboard"))

#         # ✅ Query only matching section & date range
#         closing_session = (
#             ClosingSession.query.filter(
#                 ClosingSession.section == combined_section,
#                 ClosingSession.session_date >= start_date,
#                 ClosingSession.session_date <= end_date,
#             )
#             .order_by(ClosingSession.id.desc())
#             .first()
#         )

#         if closing_session:
#             flash(message="Access granted ✅", category="success")
#             return redirect(
#                 url_for(endpoint=
#                     "super_admin_secure.edit_session",
#                     session_id=closing_session.id,
#                     sel=combined_section,
#                 )
#             )

#         # ❌ No session found
#         flash(message="No matching session found for your selection ❌", category="error")
#         return redirect(url_for(endpoint="super_admin_secure.secure_adashboard"))

#     # GET request → show modal page
#     return render_template("access_control.html", access_form=form)


@access_control_bp.route(rule="/account_mgr/verify_pin", methods=["POST"])
def verify_pin():
    try:
        validate_csrf(request.form.get("csrf_token"))
    except CSRFError:
        return {"valid": False, "error": "CSRF failed"}

    pin = request.form.get("pin", "")

    if not current_user or not current_user.password:
        return {"valid": False}

    return {"valid": bcrypt.check_password_hash(current_user.password, pin)}


@access_control_bp.route(rule="/account_mgr/access_control", methods=["GET", "POST"])
def access_control():
    form = AccessControlForm()

    if form.validate_on_submit():

        admin_pin = form.admin_pin.data

        # ✅ Validate password BEFORE doing anything else
        if not current_user or not current_user.password or not admin_pin:
            flash(message="Admin PIN required", category="danger")
            return redirect(url_for(endpoint="super_admin_secure.secure_adashboard"))

        # ✅ Use Bcrypt to verify
        if not bcrypt.check_password_hash(current_user.password, admin_pin):
            flash(message="Invalid Admin PIN", category="error")
            return redirect(url_for(endpoint="super_admin_secure.secure_adashboard"))

        # ✅ PIN correct — continue
        access_type = form.access.data.lower()
        start_date = form.start_date.data
        end_date = form.end_date.data

        access_map = {
            "s1-s2": "S1S2",
            "s3-s4": "S3S4",
            "d1-d4": "D1D4",
        }

        combined_section = access_map.get(access_type)

        if not combined_section:
            flash(message="Invalid selection", category="error")
            return redirect(url_for(endpoint="super_admin_secure.secure_adashboard"))

        closing_session = (
            ClosingSession.query.filter(
                ClosingSession.section == combined_section,
                ClosingSession.session_date >= start_date,
                ClosingSession.session_date <= end_date,
            )
            .order_by(ClosingSession.id.desc())
            .first()
        )

        if closing_session:
            flash(message="Access granted", category="success")
            return redirect(
                url_for(
                    endpoint="super_admin_secure.edit_session",
                    session_id=closing_session.id,
                    sel=combined_section,
                )
            )

        flash(message="No matching session found", category="error")
        return redirect(url_for(endpoint="super_admin_secure.secure_adashboard"))

    return render_template("access_control.html", access_form=form)


# LIST + CREATE
@access_control_bp.route(rule="/account_mgr/daily_report", methods=["GET", "POST"])
def daily_report():
    form = DailyReportForm()

    if form.validate_on_submit():
        new_report = DailyReport(
            report_title=form.report_title.data,
            report_body=form.report_body.data,
        )
        db.session.add(new_report)
        db.session.commit()
        flash(message="Daily report submitted successfully", category="success")
        return redirect(url_for(endpoint="access_control.daily_report"))

    reports = DailyReport.query.order_by(DailyReport.id.desc()).all()
    return render_template("report_.html", report_form=form, reports=reports)


@access_control_bp.route(
    rule="/account_mgr/daily_report/edit/<int:report_id>", methods=["GET", "POST"]
)
def edit_report(report_id):
    daily_report = DailyReport.query.get_or_404(report_id)
    report_form = DailyReportForm(obj=daily_report)

    if report_form.validate_on_submit():
        daily_report.report_title = report_form.report_title.data
        daily_report.report_body = report_form.report_body.data
        db.session.commit()

        flash("Report updated successfully", "success")
        return redirect(url_for("access_control.daily_report"))

    return render_template(
        "edit_report.html", report_form=report_form, daily_report=daily_report
    )


@access_control_bp.route(
    rule="/account_mgr/daily_report/delete/<int:report_id>", methods=["GET"]
)
def delete_report(report_id):
    report = DailyReport.query.get_or_404(report_id)
    db.session.delete(report)
    db.session.commit()

    flash(message="Report deleted successfully", category="success")
    return redirect(url_for("access_control.daily_report"))
