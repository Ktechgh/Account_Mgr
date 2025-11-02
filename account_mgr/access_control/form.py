from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import (
    DateField,
    SubmitField,
    SelectField,
    PasswordField,
    TextAreaField,
    StringField,
)


class UpperCaseField(StringField):
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0].title()
        else:
            self.data = ""


class UpperTextArea(TextAreaField):
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0].title()
        else:
            self.data = ""


class AccessControlForm(FlaskForm):
    access = SelectField(
        validators=[DataRequired()],
        choices=[
            ("", "-- Select Access Type --"),
            ("s1-s2", "S1-S2"),
            ("s3-s4", "S3-S4"),
            ("d1-d4", "D1-d4"),
        ],
        coerce=str,
    )
    start_date = DateField(
        label="Start Date", format="%Y-%m-%d", validators=[DataRequired()]
    )
    end_date = DateField(
        label="End Date", format="%Y-%m-%d", validators=[DataRequired()]
    )
    admin_pin = PasswordField(validators=[DataRequired()])
    submit = SubmitField(label="Grant Access")


class DailyReportForm(FlaskForm):
    report_title = UpperCaseField(
        label="Report Title",
        validators=[DataRequired()],
        render_kw={"placeholder": "Enter Report Title"},
    )
    report_body = UpperTextArea(
        label="Report Body",
        validators=[DataRequired()],
        render_kw={"placeholder": "Enter Report Details", "rows": 5},
    )
    submit = SubmitField(label="Submit Report")
