from flask_login import logout_user
from account_mgr import db, bcrypt, app
from flask_mailman import EmailMessage
from account_mgr.database.models import User
from flask_login import current_user, login_required
from account_mgr.media_utils.utils import save_user_picture
from .form import UpdateAccount, RequestResetForm, ResetPasswordForm
from flask import render_template, Blueprint, request, redirect, flash, url_for


account_ = Blueprint(
    "account_", __name__, template_folder="templates", static_folder="static"
)


@account_.route(rule="account_mgr/account_mgr/account", methods=["GET", "POST"])
@login_required
def secure_account_update():
    form = UpdateAccount()

    if form.validate_on_submit():
        # Handle profile picture update
        if form.picture.data:
            picture_file = save_user_picture(form_picture=form.picture.data)
            current_user.user_profile = picture_file

        # Update email and username
        current_user.email = form.email.data
        current_user.username = form.username.data

        # Handle password update only if a new password is provided
        if form.password.data:
            if form.password.data == form.confirm_password.data:
                hashed_password = bcrypt.generate_password_hash(
                    form.password.data
                ).decode("utf-8")
                current_user.password = hashed_password
            else:
                flash(message="Passwords do not match.", category="error")
                return redirect(url_for(endpoint="account_.secure_account_update"))

        # 🔒 Check if it was a default credential before update
        was_default = current_user.is_default_credential

        # Mark as no longer default
        current_user.is_default_credential = False

        # Preserve role before logout
        user_role = current_user.user_role
        is_super_admin = current_user.is_super_admin
        db.session.commit()
        flash(
            message="Your account has been updated!"
            + (" Please log in again." if was_default and (is_super_admin or user_role == "Admin") else ""),
            category="success",
        )

        # 🔐 Log out only if:
        # - the user was using default credentials
        # - and is an Admin or Super Admin
        if was_default and (is_super_admin or user_role == "Admin"):
            logout_user()
            if is_super_admin or user_role == "Admin":
                return redirect(url_for(endpoint="super_admin_secure.secure_superlogin"))
            else:
                return redirect(url_for(endpoint="view.user_secure_dashboard"))

        # ✅ Otherwise, redirect to dashboard without logout
        if is_super_admin or user_role == "Admin":
            return redirect(url_for(endpoint="super_admin_secure.secure_adashboard"))
        else:
            return redirect(url_for(endpoint="view.user_secure_dashboard"))

    elif request.method == "GET":
        form.email.data = current_user.email
        form.username.data = current_user.username

    # Display form errors
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(message=f"Error in {field}: {error}", category="error")

    return render_template("update_account.html", form=form)


def send_reset_email(user):
    token = user.get_reset_token()  # call it on the instance
    try:
        msg = EmailMessage(
            body=f"To reset your password, visit the following link: {url_for(endpoint='account_.reset_token', token=token, _external=True)}",
            subject="Password Reset Request",
            from_email=app.config["MAIL_USERNAME"],
            to=[user.email],
        )
        msg.send()
        return True
    except Exception:
        flash(
            message="We couldn't send the reset email. Please try again later",
            category="error",
        )
        return False  # Explicit failure


@account_.route(rule="/account_mgr/account/reset-request", methods=["GET", "POST"])
@login_required
def reset_request():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if send_reset_email(user):
            flash(
                message="An email has been sent with instructions to reset your password",
                category="success",
            )
        return redirect(url_for(endpoint="account_.reset_request"))
    return render_template("request_reset.html", form=form)


@account_.route(
    rule="/account_mgr/account/password-reset/<token>", methods=["GET", "POST"]
)
def reset_token(token):
    form = ResetPasswordForm()
    user = User.verify_reset_token(token)

    if user is None:
        flash(message="That is an invalid or expired token", category="error")
        return redirect(url_for(endpoint="account_.reset_request"))

    if form.validate_on_submit():
        hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_pwd
        db.session.commit()
        flash(message="Your password has been updated", category="success")

        redirect_endpoint = (
            "super_admin_secure.secure_adashboard"
            if user.is_super_admin or user.user_role == "Admin"
            else "view.user_secure_dashboard"
        )

        return redirect(url_for(endpoint=redirect_endpoint))

    return render_template("reset_token.html", form=form)
