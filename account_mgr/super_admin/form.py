from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Optional
from wtforms import (
    DateField,
    SelectField,
    SubmitField,
    StringField,
    EmailField,
    DecimalField,
    IntegerField,
    PasswordField,
    HiddenField,
)


class UpperRoleField(StringField):
    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0].title()
        else:
            self.data = ""


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


class SectionForm(FlaskForm):
    section = SelectField(
        label="Choose Meter To Activate Table:",
        choices=[
            ("", "-- Select --"),
            ("S1S2", "S1 & S2"),
            ("S3S4", "S3 & S4"),
            ("D1D4", "D1 & D4"),
            ("stock", "Stock"),
        ],
        default="",
        validators=[DataRequired(message="⚠️ Please select a meter table.")],
    )


class LoginForm(FlaskForm):
    email = EmailField(validators=[DataRequired()], render_kw={"placeholder": "Email"})
    username = StringField(
        validators=[DataRequired()], render_kw={"placeholder": "Username"}
    )
    password = PasswordField(
        validators=[DataRequired()], render_kw={"placeholder": "Password"}
    )
    login = SubmitField(label="Submit")


# ---------------- METER READING FORM ----------------
class Super12Form(FlaskForm):
    section = HiddenField(label="section")
    super_1_opening = DecimalField(
        places=2, validators=[DataRequired()], render_kw={"placeholder": "S1 (Opening)"}
    )
    super_2_opening = DecimalField(
        places=2, validators=[DataRequired()], render_kw={"placeholder": "S2 (Opening)"}
    )
    super_1_closing = DecimalField(
        places=2, validators=[DataRequired()], render_kw={"placeholder": "S1 (Closing)"}
    )
    super_2_closing = DecimalField(
        places=2, validators=[DataRequired()], render_kw={"placeholder": "S2 (Closing)"}
    )
    gsa_test_draw = DecimalField(
        label="RTT",
        places=2,
        validators=[Optional()],
        render_kw={"placeholder": "RTT (Liters)"},
    )
    liters_sold = DecimalField(
        places=2,
        validators=[DataRequired()],
        render_kw={"readonly": True, "placeholder": "Liters Sold"},
    )

    price = DecimalField(
        places=2, validators=[DataRequired()], render_kw={"placeholder": "Enter Price"}
    )
    total = DecimalField(
        label="Total",
        places=2,
        validators=[DataRequired()],
        render_kw={"readonly": True, "placeholder": "Total Amount"},
    )
    date_of_sale = DateField(
        label="Sale Date", format="%Y-%m-%d", validators=[DataRequired()]
    )
    csa_name = SelectField(
        coerce=str,
        validators=[DataRequired()],
        render_kw={
            "class": "form-select",
            "aria-label": "CSA Name",
        },
    )

    submit_meter = SubmitField(label="Submit S1-S2")
    submit_s3s4 = SubmitField(label="Submit S3-S4")


class D14Form(FlaskForm):
    d1_opening = DecimalField(
        places=2, validators=[DataRequired()], render_kw={"placeholder": "D1 (Opening)"}
    )
    d1_closing = DecimalField(
        places=2, validators=[DataRequired()], render_kw={"placeholder": "D1 (Closing)"}
    )
    d2_opening = DecimalField(
        places=2, validators=[DataRequired()], render_kw={"placeholder": "D2 (Opening)"}
    )
    d2_closing = DecimalField(
        places=2, validators=[DataRequired()], render_kw={"placeholder": "D2 (Closing)"}
    )
    d3_opening = DecimalField(
        places=2, validators=[DataRequired()], render_kw={"placeholder": "D3 (Opening)"}
    )
    d3_closing = DecimalField(
        places=2, validators=[DataRequired()], render_kw={"placeholder": "D3 (Closing)"}
    )
    d4_opening = DecimalField(
        places=2, validators=[DataRequired()], render_kw={"placeholder": "D4 (Opening)"}
    )
    d4_closing = DecimalField(
        places=2, validators=[DataRequired()], render_kw={"placeholder": "D4 (Closing)"}
    )
    rtt_liters = DecimalField(
        label="RTT",
        places=2,
        validators=[Optional()],
        render_kw={"placeholder": "RTT (Liters)"},
    )
    liters_sold = DecimalField(
        places=2,
        validators=[DataRequired()],
        render_kw={"readonly": True, "placeholder": "Liters Sold"},
    )
    price = DecimalField(
        places=2, validators=[DataRequired()], render_kw={"placeholder": "Enter Price"}
    )
    total = DecimalField(
        label="Total",
        places=2,
        validators=[DataRequired()],
        render_kw={"readonly": True, "placeholder": "Total Amount"},
    )
    date_of_sale = DateField(
        label="Sale Date", format="%Y-%m-%d", validators=[DataRequired()]
    )
    csa_name = SelectField(
        coerce=str,
        validators=[DataRequired()],
        render_kw={
            "class": "form-select",
            "aria-label": "CSA Name",
        },
    )
    submit_d1d4 = SubmitField(label="Submit D1-D4")


# ---------------- E-CASH/CREDIT TRANSACTION FORM ----------------
class CreditTransactionForm(FlaskForm):
    gcb = DecimalField(
        places=2, validators=[Optional()], render_kw={"placeholder": "GCB"}
    )
    momo = DecimalField(
        places=2, validators=[Optional()], render_kw={"placeholder": "MoMo"}
    )
    tingg = DecimalField(
        places=2, validators=[Optional()], render_kw={"placeholder": "Tingg"}
    )
    zenith = DecimalField(
        places=2, validators=[Optional()], render_kw={"placeholder": "Zenith"}
    )
    republic = DecimalField(
        places=2, validators=[Optional()], render_kw={"placeholder": "Republic"}
    )
    prudential = DecimalField(
        places=2, validators=[Optional()], render_kw={"placeholder": "Prudential"}
    )
    adb = DecimalField(
        places=2, validators=[Optional()], render_kw={"placeholder": "ADB"}
    )
    stanbic = DecimalField(
        places=2, validators=[Optional()], render_kw={"placeholder": "Stanbic"}
    )
    ecobank = DecimalField(
        places=2, validators=[Optional()], render_kw={"placeholder": "Ecobank"} 
    )
    fidelity = DecimalField(    
        places=2, validators=[Optional()], render_kw={"placeholder": "Fidelity"}
    )
    credit_ab = DecimalField(
        places=2,
        validators=[Optional()],
        render_kw={"placeholder": "Credit Sale (Mr Ablor)"},
    )
    credit_cf = DecimalField(
        places=2,
        validators=[Optional()],
        render_kw={"placeholder": "Credit Sale (Cassava Farm)"},
    )
    credit_wl = DecimalField(
        places=2,
        validators=[Optional()],
        render_kw={"placeholder": "Credit Sale (Williago)"},
    )
    credit_zl = DecimalField(
        places=2,
        validators=[Optional()],
        render_kw={"placeholder": "Credit Sale (Zoomlion)"},
    )
    soc_staff_credit = DecimalField(
        places=2,
        validators=[Optional()],
        render_kw={"placeholder": "Approved Credit (Soc Staff)"},
    )
    water_bill = DecimalField(
        places=2, validators=[Optional()], render_kw={"placeholder": "Water Bill"}
    )
    ecg_bill = DecimalField(
        places=2, validators=[Optional()], render_kw={"placeholder": "ECG Bill"}
    )
    genset = DecimalField(
        places=2, validators=[Optional()], render_kw={"placeholder": "Genset"}
    )
    approve_miscellaneous = DecimalField(
        places=2,
        validators=[Optional()],
        render_kw={"placeholder": "Approved Miscellaneous"},
    )
    collection_zl = DecimalField(
        places=2,
        validators=[Optional()],
        render_kw={"placeholder": "Collection (Zoomlion)"},
    )
    credit_gc = DecimalField(
        places=2,
        validators=[Optional()],
        render_kw={"placeholder": "Credit Sale (Gadco)"},
    )
    collection_gc = DecimalField(
        places=2,
        validators=[Optional()],
        render_kw={"placeholder": "Collection (Gadco)"},
    )
    collection_ab = DecimalField(
        places=2,
        validators=[Optional()],
        render_kw={"placeholder": "Collection (Ablor)"},
    )
    collection_cv = DecimalField(
        places=2,
        validators=[Optional()],
        render_kw={"placeholder": "Collection (Cassava Farm)"},
    )
    collection_wl = DecimalField(
        places=2,
        validators=[Optional()],
        render_kw={"placeholder": "Collection (Williago)"},
    )
    lube_1_liter = DecimalField(
        places=2, validators=[Optional()], render_kw={"placeholder": "Lube (1L)"}
    )
    lube_drum = DecimalField(
        places=2, validators=[Optional()], render_kw={"placeholder": "Drum Lube"}
    )
    duster_collection = DecimalField(
        places=2,
        validators=[Optional()],
        render_kw={"placeholder": "Duster Collection"},
    )

    # New readonly fields for totals
    total_credit = DecimalField(
        places=2, validators=[Optional()], render_kw={"readonly": True}
    )
    total_collection = DecimalField(  
        places=2,
        validators=[Optional()],
        render_kw={"readonly": True, "class": "form-control light-green"},
    )
    cash_to_bank = DecimalField(
        places=2, validators=[Optional()], render_kw={"readonly": True}
    )
    grand_total = DecimalField(
        places=2, validators=[Optional()], render_kw={"readonly": True}
    )
    paper_total = DecimalField(
        places=2,
        validators=[Optional()],
        render_kw={"readonly": True, "class": "form-control light-green"},
    )
    coin_total = DecimalField(
        places=2,
        validators=[Optional()],
        render_kw={"readonly": True, "class": "form-control light-green"},
    )
    total_physical_cash = DecimalField(
        places=2,
        validators=[Optional()],
        render_kw={"readonly": True, "class": "form-control light-green"},
    )
    cash_balance_status = StringField(
        validators=[Optional()], render_kw={"readonly": True, "class": "form-control"}
    )

    submit_credit = SubmitField(label="Save E-Cash & Credit")


# ---------------- PAPER TRANSACTION FORM ----------------
class PaperDinominationForm(FlaskForm):
    note_200 = IntegerField(
        validators=[Optional()], render_kw={"placeholder": "₵200 notes"}
    )
    note_100 = IntegerField(
        validators=[Optional()], render_kw={"placeholder": "₵100 notes"}
    )
    note_50 = IntegerField(
        validators=[Optional()],
        render_kw={"placeholder": "₵50 notes", "data-denom": 50},
    )
    note_20 = IntegerField(
        validators=[Optional()], render_kw={"placeholder": "₵20 notes"}
    )
    note_10 = IntegerField(
        validators=[Optional()], render_kw={"placeholder": "₵10 notes"}
    )
    note_5 = IntegerField(
        validators=[Optional()], render_kw={"placeholder": "₵5 notes"}
    )
    note_2 = IntegerField(
        validators=[Optional()], render_kw={"placeholder": "₵2 notes"}
    )
    note_1 = IntegerField(
        validators=[Optional()], render_kw={"placeholder": "₵1 notes"}
    )


# ---------------- COINS TRANSACTION FORM ----------------
class CoinsDinominationForm(FlaskForm):
    # section = HiddenField(label="section")
    coin_5 = IntegerField(
        validators=[Optional()], render_kw={"placeholder": "₵0.50 coin"}
    )
    coin_2 = IntegerField(validators=[Optional()], render_kw={"placeholder": "₵2 coin"})
    coin_1 = IntegerField(validators=[Optional()], render_kw={"placeholder": "₵1 coin"})
