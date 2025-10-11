from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import (
    SubmitField,
    StringField,
)


class UpperRoleField(StringField):
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0].title()
        else:
            self.data = ""


class AttendantForm(FlaskForm):
    attendant_name = UpperRoleField(
        label="Name",
        validators=[DataRequired()],
        render_kw={"placeholder": "Enter CSAs Name"},
    )
    submit = SubmitField()
