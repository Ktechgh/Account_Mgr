import traceback
from flask import session
from account_mgr import app
from http import HTTPStatus
from flask_wtf.csrf import CSRFError
from flask import render_template, Blueprint, flash, redirect, url_for


errors_ = Blueprint(
    "errors_", __name__, template_folder="templates", static_folder="static"
)


@errors_.errorhandler(CSRFError)
def handle_csrf_error(error):
    flash(message="Your session expired. Please log in again!", category="error")
    session.modified = True 
    return redirect(url_for(endpoint="super_admin_secure.secure_superlogin"))


@errors_.app_errorhandler(400)
def bad_request(error):
    app.logger.error(msg=f"400 Error: {error}\n{traceback.format_exc()}")

    # Case 1: User session missing or expired
    if "_user_id" not in session:
        session.clear()
        flash(
            message="Your session has expired. Please log in again", category="error"
        )
        return redirect(url_for(endpoint="super_admin_secure.secure_superlogin"))

    # Case 2: Genuine bad request
    flash(
        message="Bad request. Please check your input and try again.", category="error"
    )
    return render_template("bad_request.html"), HTTPStatus.BAD_REQUEST


@errors_.app_errorhandler(401)
def un_authorized(error):
    return render_template("unauthorized.html"), HTTPStatus.UNAUTHORIZED


@errors_.app_errorhandler(403)
def forbidden_error(error):
    return render_template("forbidden.html"), HTTPStatus.FORBIDDEN


@errors_.app_errorhandler(404)
def not_found_error(error):
    return render_template("not_found.html"), HTTPStatus.NOT_FOUND


@errors_.app_errorhandler(413)
def payload_too_large_error(error):
    return render_template("payload_data.html"), HTTPStatus.CONTENT_TOO_LARGE


@errors_.app_errorhandler(429)
def too_many_requests_error(error):
    flash(message="Too many request, try again in a few minutes", category="error")
    return render_template("too_many_requests.html"), HTTPStatus.TOO_MANY_REQUESTS


@errors_.app_errorhandler(500)
def internal_server_error(error):
    return (
        render_template("internal_server.html"),
        HTTPStatus.INTERNAL_SERVER_ERROR,
    )


@errors_.app_errorhandler(ValueError)
def value_error(error):
    error_message = session.pop("error_message", None)
    if error_message:
        app.logger.error(msg=error_message)
    else:
        app.logger.error(msg=f"Error occurred: {error}")
    return render_template("invalid_path.html")


def maintainance():
    # Your logic here
    pass


@errors_.app_errorhandler(503)
def app_maintenance_mode(error):  # Optional prefix for consistency
    if maintainance:  # Replace with your logic to check maintenance mode
        return render_template("maintenance.html"), HTTPStatus.SERVICE_UNAVAILABLE
    # Code to handle other 503 errors (optional)
    return None  # Fallback for non-maintenance related 503 errors
