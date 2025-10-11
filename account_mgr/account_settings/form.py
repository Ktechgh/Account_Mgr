from flask_wtf import FlaskForm
from flask_login import current_user
from account_mgr.database.models import User
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import (
    Length,
    Email,
    EqualTo,
    Optional,
    DataRequired,
    InputRequired,
    ValidationError,
)


class UpdateAccount(FlaskForm):
    """Form for updating user account."""
    email = EmailField(
        validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"}
    )
    
    username = StringField(validators=[DataRequired()])

    picture = FileField(validators=[FileAllowed(["jpg", "png"])])
    
    password = PasswordField(
        validators=[Optional(), Length(min=4, max=15)],
        render_kw={"placeholder": "Password"},
    )
    
    confirm_password = PasswordField(
        validators=[Optional(), EqualTo("password", message="Passwords must match.")],
        render_kw={"placeholder": "Confirm_Password"},
    )
    
    submit = SubmitField(label="Update")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    message="That username already exists! Please choose a different username."
                )
                
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    message="That email already exist! Choose different one"
                )


class RequestResetForm(FlaskForm):
    """Form for requesting a password reset."""
    email = EmailField(
        validators=[DataRequired(), Email()], render_kw={"placeholder": "Enter your email"}
    )

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(message="There is no account with that email")

    submit = SubmitField(label="Request Reset")


class ResetPasswordForm(FlaskForm):
    """Form for resetting the password."""
    password = PasswordField(
        validators=[DataRequired(message="Enter password"), Length(min=4, max=15)],
        render_kw={"placeholder": "Password"},
    )
    
    confirm_password = PasswordField(
        validators=[
            InputRequired(),
            EqualTo("password", message="Password must match"),
        ],
        render_kw={"placeholder": "Repeat Password"},
    )
    
    submit = SubmitField(label="Reset Password")
