from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import SubmitField, DateField, SelectField


class TransactionReportForm(FlaskForm):
    """Form for generating transaction reports"""

    report_type = SelectField(
        label="Report Type",
        validators=[DataRequired()],
        choices=[
            ("", "-- Select Report Type --"),
            ("all", "All"),
            ("meter", "Meter Readings"),
            ("d14", "D1-D4 Diesel Readings"), 
            ("credit", "E-Cash & Credit"),
            ("paper", "Paper Denomination"),
            ("coins", "Coins Denomination"),
            ("closing", "Closing Session"),
        ],
        coerce=str,
    )

    start_date = DateField(
        label="Start Date",
        format="%Y-%m-%d",
        validators=[DataRequired()],
    )
    end_date = DateField(
        label="End Date",
        format="%Y-%m-%d",
        validators=[DataRequired()],
    )
    submit = SubmitField(label="Generate Report")


class CashSummaryForm(FlaskForm):
    """Form for generating cash summary reports"""

    cash_report_type = SelectField(
        label="Report Type",
        validators=[DataRequired()],
        choices=[
            ("", "-- Select Report Type --"),
            ("all", "All (Paper + Coins)"),
            ("paper", "Paper Denominations Only"),
            ("coins", "Coins Denominations Only"),
        ],
        coerce=str,
    )

    start_date = DateField(
        label="Start Date",
        format="%Y-%m-%d",
        validators=[DataRequired()],
    )
    end_date = DateField(
        label="End Date",
        format="%Y-%m-%d",
        validators=[DataRequired()],
    )
    submit = SubmitField(label="Generate Report")


class PerPageForm(FlaskForm):
    per_page = SelectField(
        label="Show",
        choices=[
            ("2", "2"),
            ("5", "5"),
            ("10", "10"),
            ("25", "25"),
            ("50", "50"),
            ("100", "100"),
        ],
        default="5",
        render_kw={"class": "form-select form-select-sm w-auto me-2"},
    )
