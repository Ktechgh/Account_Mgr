import os
from datetime import date
from decimal import Decimal
from functools import wraps
from dotenv import load_dotenv
from sqlalchemy import inspect
from flask_wtf.csrf import generate_csrf
from account_mgr import db, bcrypt, logging
from .form import (
    D14Form,
    LoginForm,
    PerPageForm,
    SectionForm,
    Super12Form,
    CreditTransactionForm,
    PaperDinominationForm,
    CoinsDinominationForm,
)
from flask_login import current_user, login_required, login_user, logout_user
from flask import (
    current_app,
    render_template,
    session,
    url_for,
    flash,
    redirect,
    Blueprint,
    request,
    abort,
)
from account_mgr.database.models import (
    User,
    Tenant,
    CSAName,
    D14Reading,
    MeterReading,
    ClosingSession,
    PaperTransaction,
    CoinsTransaction,
    CreditTransaction,
)


super_admin_secure = Blueprint(
    import_name=__name__,
    name="super_admin_secure",
    template_folder="templates",
    static_folder="static",
)

load_dotenv()
admin_username = os.getenv("ADMIN_USERNAME")
admin_password = os.getenv("ADMIN_PASSWORD")


def super_admin_required(f):
    """Decorator to ensure the user is authenticated and is a super admin."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_super_admin:
            abort(code=403)
        return f(*args, **kwargs)

    return decorated_function


def seed_super_admin():
    """Seed the default tenant and super admin if they do not exist."""
    try: 
        # Step 1: Ensure a tenant exists
        tenant = Tenant.query.first()
        if not tenant:
            tenant = Tenant(
                business_name="Esvid Mart",
                shop_code="0000",
                email="esvid@gmail.com",
                phone="0200000000",
                address="Default Address",
            )
            db.session.add(tenant)
            db.session.commit()
            logging.info("✅ Default tenant created.")

        # Step 2: Ensure super admin exists
        existing_admin = User.query.filter(
            (User.email == "admin@example.com")
            | (User.staff_id == "admin0001")
            | (User.username == admin_username)
        ).first()

        if existing_admin:
            logging.info("ℹ️ Super admin already exists. Skipping creation.")
            return

        admin = User(
            username=admin_username,
            staff_id="admin0001",
            password=bcrypt.generate_password_hash(admin_password).decode("utf-8"),
            user_role="SuperUser",
            email="admin@example.com",
            user_profile="default.jpg",
            is_super_admin=True,
            tenant_id=tenant.id,
        )
        db.session.add(admin)
        db.session.commit()
        logging.info("✅ Super admin seeded successfully.")

    except Exception as e:
        db.session.rollback()
        logging.error(f"❌ Error seeding super admin: {e}")


@super_admin_secure.route(rule="/", methods=["GET", "POST"])
def secure_superlogin():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(
            email=form.email.data, username=form.username.data
        ).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if user.is_super_admin:
                login_user(user)
                # session.permanent = True  # Keep session alive as per your config

                if user.is_default_credential:
                    flash(
                        message="Please update your account details to proceed.",
                        category="error",
                    )
                    return redirect(url_for(endpoint="account_.secure_account_update"))

                flash(message=f"Login Successfully {user.username}", category="success")
                return redirect(
                    url_for(endpoint="super_admin_secure.secure_adashboard")
                )

            else:
                flash(
                    message="You are not authorized to access this page.",
                    category="error",
                )
                return redirect(
                    url_for(endpoint="super_admin_secure.secure_superlogin")
                )

        else:
            flash(message="Invalid email/username or Password", category="error")

    csrf_token = generate_csrf()
    form.csrf_token.data = csrf_token

    # 🔹 Debug log to console
    print(f"🔑 New CSRF Token generated: {csrf_token}")
    return render_template("login_layout.html", form=form)


@super_admin_secure.route(rule="account_mgr/secure_adashboard", methods=["GET", "POST"])
@login_required
def secure_adashboard():
    # Forms
    d1d4_form = D14Form(prefix="d1d4")
    section_form = SectionForm()
    per_page_form = PerPageForm()
    s1s2_form = Super12Form(prefix="s1s2")
    s3s4_form = Super12Form(prefix="s3s4")
    credit_form = CreditTransactionForm()
    paper_form = PaperDinominationForm()
    coins_form = CoinsDinominationForm()

    # It auto-resets every midnight (new day → new entries).
    closing_sessions = ClosingSession.query.filter_by(session_date=date.today()).all()

    # Populate CSA Name dropdown for each form
    csa_choices = [("0", "--Select CSA Name--")] + [
        (str(c.id), c.attendant_name) for c in CSAName.query.all()
    ]

    for form in [s1s2_form, s3s4_form, d1d4_form]:
        if hasattr(form, "csa_name"):
            form.csa_name.choices = csa_choices

    def get_session_for_section(section, username, create_if_missing=False):
        today = date.today()

        closing_session = ClosingSession.query.filter_by(
            section=section, session_date=today
        ).first()

        # Only create session if explicitly allowed
        if not closing_session and create_if_missing:
            closing_session = ClosingSession(
                section=section, admin_user_name=username, session_date=today
            )
            db.session.add(closing_session)
            db.session.commit()

        return closing_session

    if request.method == "POST":
        # ----------------- METER READING: S1 & S2 -----------------
        if "s1s2-submit_meter" in request.form and s1s2_form.validate_on_submit():
            try:
                s1_opening = s1s2_form.super_1_opening.data or Decimal(value=0)
                s2_opening = s1s2_form.super_2_opening.data or Decimal(value=0)
                s1_closing = s1s2_form.super_1_closing.data or Decimal(value=0)
                s2_closing = s1s2_form.super_2_closing.data or Decimal(value=0)
                gsa_test_draw = s1s2_form.gsa_test_draw.data or Decimal(value=0)

                if len(str(s1_closing)) < 8 or len(str(s2_closing)) < 8:
                    flash(
                        message="Please enter complete closing meter readings for S1S2",
                        category="error",
                    )
                    return redirect(
                        url_for(endpoint="super_admin_secure.secure_adashboard")
                    )

                price = s1s2_form.price.data or Decimal(value=0)
                liters_sold = (
                    (s1_closing - s1_opening)
                    + (s2_closing - s2_opening)
                    - gsa_test_draw
                )
                total = liters_sold * price

                closing_session = get_session_for_section(
                    section="S1S2",
                    username=current_user.username,
                    create_if_missing=True,
                )

                csa = CSAName.query.get(int(s1s2_form.csa_name.data))
                meter_reading = MeterReading(
                    section="S1S2",
                    super_1_opening=s1_opening,
                    super_2_opening=s2_opening,
                    super_1_closing=s1_closing,
                    super_2_closing=s2_closing,
                    gsa_test_draw=gsa_test_draw,
                    liters_sold=liters_sold,
                    price=price,
                    total=total,
                    date_of_sale=s1s2_form.date_of_sale.data,
                    csa_name=csa.attendant_name if csa else "",
                    session_id=closing_session.id,
                )
                db.session.add(meter_reading)
                db.session.commit()
                flash(message="S1 & S2 meter reading saved!", category="success")
            except Exception as e:
                db.session.rollback()
                flash(
                    message=f"Error saving S1S2 meter reading: {str(e)}",
                    category="error",
                )

            return redirect(url_for(endpoint="super_admin_secure.secure_adashboard"))

        # ----------------- METER READING: S3 & S4 -----------------
        elif "s3s4-submit_s3s4" in request.form and s3s4_form.validate_on_submit():
            try:
                s3_opening = s3s4_form.super_1_opening.data or Decimal(value=0)
                s4_opening = s3s4_form.super_2_opening.data or Decimal(value=0)
                s3_closing = s3s4_form.super_1_closing.data or Decimal(value=0)
                s4_closing = s3s4_form.super_2_closing.data or Decimal(value=0)
                gsa_test_draw = s3s4_form.gsa_test_draw.data or Decimal(value=0)

                if len(str(s3_closing)) < 8 or len(str(s4_closing)) < 8:
                    flash(
                        message="Please enter complete closing meter readings for S3S4",
                        category="error",
                    )
                    return redirect(
                        url_for(endpoint="super_admin_secure.secure_adashboard")
                    )

                price = s3s4_form.price.data or Decimal(value=0)
                liters_sold = (
                    (s3_closing - s3_opening)
                    + (s4_closing - s4_opening)
                    - gsa_test_draw
                )
                total = liters_sold * price

                closing_session = get_session_for_section(
                    section="S3S4",
                    username=current_user.username,
                    create_if_missing=True,
                )

                csa = CSAName.query.get(int(s3s4_form.csa_name.data))
                meter_reading = MeterReading(
                    section="S3S4",
                    super_1_opening=s3_opening,
                    super_2_opening=s4_opening,
                    super_1_closing=s3_closing,
                    super_2_closing=s4_closing,
                    gsa_test_draw=gsa_test_draw,
                    liters_sold=liters_sold,
                    price=price,
                    total=total,
                    date_of_sale=s3s4_form.date_of_sale.data,
                    csa_name=csa.attendant_name if csa else "",
                    session_id=closing_session.id,
                )
                db.session.add(meter_reading)
                db.session.commit()
                flash(message="S3 & S4 meter reading saved!", category="success")
            except Exception:
                db.session.rollback()
                flash(message=f"Error saving S3S4 meter reading:", category="error")

            return redirect(url_for(endpoint="super_admin_secure.secure_adashboard"))

        # ----------------- METER READING: D1–D4 -----------------
        elif "d1d4-submit_d1d4" in request.form and d1d4_form.validate_on_submit():
            try:
                d1_opening = d1d4_form.d1_opening.data or Decimal(value=0)
                d1_closing = d1d4_form.d1_closing.data or Decimal(value=0)
                d2_opening = d1d4_form.d2_opening.data or Decimal(value=0)
                d2_closing = d1d4_form.d2_closing.data or Decimal(value=0)
                d3_opening = d1d4_form.d3_opening.data or Decimal(value=0)
                d3_closing = d1d4_form.d3_closing.data or Decimal(value=0)
                d4_opening = d1d4_form.d4_opening.data or Decimal(value=0)
                d4_closing = d1d4_form.d4_closing.data or Decimal(value=0)
                rtt_liters = d1d4_form.rtt_liters.data or Decimal(value=0)

                if len(str(d1_closing)) < 8 or len(str(d2_closing)) < 8:
                    flash(
                        message="Please enter complete closing meter readings for D1-D4",
                        category="error",
                    )
                    return redirect(
                        url_for(endpoint="super_admin_secure.secure_adashboard")
                    )

                price = d1d4_form.price.data or Decimal(value=0)
                liters_sold = (
                    (d1_closing - d1_opening)
                    + (d2_closing - d2_opening)
                    + (d3_closing - d3_opening)
                    + (d4_closing - d4_opening)
                    - rtt_liters
                )
                total = liters_sold * price

                # closing_session = get_session_for_section("D1D4", current_user.username)
                closing_session = get_session_for_section(
                    section="D1D4",
                    username=current_user.username,
                    create_if_missing=True,
                )

                csa = CSAName.query.get(int(d1d4_form.csa_name.data))
                d14_reading = D14Reading(
                    section="D1D4",
                    d1_opening=d1_opening,
                    d1_closing=d1_closing,
                    d2_opening=d2_opening,
                    d2_closing=d2_closing,
                    d3_opening=d3_opening,
                    d3_closing=d3_closing,
                    d4_opening=d4_opening,
                    d4_closing=d4_closing,
                    rtt_liters=rtt_liters,
                    liters_sold=liters_sold,
                    price=price,
                    total=total,
                    date_of_sale=d1d4_form.date_of_sale.data,
                    csa_name=csa.attendant_name if csa else "",
                    session_id=closing_session.id,
                )
                db.session.add(d14_reading)
                db.session.commit()
                flash(message="D1-D4 diesel meter reading saved!", category="success")
            except Exception as e:
                db.session.rollback()
                flash(message=f"Error saving D1D4 meter reading", category="error")

            return redirect(url_for(endpoint="super_admin_secure.secure_adashboard"))

        # ----------------- CREDIT TRANSACTION -----------------
        elif "submit_credit" in request.form and credit_form.validate_on_submit():
            try:
                selected_section = request.form.get(
                    key="selected_section", default="S1S2"
                )

                closing_session = get_session_for_section(
                    selected_section, current_user.username, create_if_missing=False
                )

                if not closing_session:
                    flash(
                        message="You must first submit a meter reading before credit transactions!",
                        category="error",
                    )
                    return redirect(
                        url_for(endpoint="super_admin_secure.secure_adashboard")
                    )

                # 🔹 Check for existing credit record
                existing_credit = CreditTransaction.query.filter_by(
                    session_id=closing_session.id
                ).first()
                if existing_credit:
                    flash(
                        message="Credit transaction already submitted for this session!",
                        category="error",
                    )
                    return redirect(
                        url_for(endpoint="super_admin_secure.secure_adashboard")
                    )

                # Safely default empty decimals to 0
                gcb = credit_form.gcb.data or Decimal(0)
                momo = credit_form.momo.data or Decimal(0)
                tingg = credit_form.tingg.data or Decimal(0)
                zenith = credit_form.zenith.data or Decimal(0)

                # 🏦 New Banks
                republic = credit_form.republic.data or Decimal(0)
                prudential = credit_form.prudential.data or Decimal(0)
                adb = credit_form.adb.data or Decimal(0)
                stanbic = credit_form.stanbic.data or Decimal(0)
                ecobank = credit_form.ecobank.data or Decimal(0)
                fidelity = credit_form.fidelity.data or Decimal(0)

                # 🧾 New Deductions under credit
                water_bill = credit_form.water_bill.data or Decimal(0)
                ecg_bill = credit_form.ecg_bill.data or Decimal(0)
                genset = credit_form.genset.data or Decimal(0)
                approve_miscellaneous = (
                    credit_form.approve_miscellaneous.data or Decimal(0)
                )

                credit_ab = credit_form.credit_ab.data or Decimal(0)
                credit_cf = credit_form.credit_cf.data or Decimal(0)
                credit_gc = credit_form.credit_gc.data or Decimal(0)
                credit_wl = credit_form.credit_wl.data or Decimal(0)
                credit_zl = credit_form.credit_zl.data or Decimal(0)
                soc_staff_credit = credit_form.soc_staff_credit.data or Decimal(0)

                collection_ab = credit_form.collection_ab.data or Decimal(0)
                collection_wl = credit_form.collection_wl.data or Decimal(0)
                collection_zl = credit_form.collection_zl.data or Decimal(0)
                collection_gc = credit_form.collection_gc.data or Decimal(0)
                collection_cv = credit_form.collection_cv.data or Decimal(0)
                lube_1_liter = credit_form.lube_1_liter.data or Decimal(0)
                lube_drum = credit_form.lube_drum.data or Decimal(0)
                duster_collection = credit_form.duster_collection.data or Decimal(0)

                total_credit = sum(
                    [
                        gcb,
                        momo,
                        tingg,
                        zenith,
                        republic,
                        prudential,
                        adb,
                        stanbic,
                        ecobank,
                        fidelity,
                        credit_ab,
                        credit_cf,
                        credit_gc,
                        credit_wl,
                        credit_zl,
                        soc_staff_credit,
                        water_bill,
                        ecg_bill,
                        genset,
                        approve_miscellaneous,
                    ]
                )

                total_collection = sum(
                    [
                        collection_ab,
                        collection_wl,
                        collection_zl,
                        collection_gc,
                        collection_cv,
                        lube_1_liter,
                        lube_drum,
                        duster_collection,
                    ]
                )

                # ----------------- Get meter total -----------------
                if selected_section in ["S1S2", "S3S4"]:
                    meter_total = (
                        db.session.query(MeterReading.total)
                        .filter_by(session_id=closing_session.id)
                        .order_by(MeterReading.id.desc())
                        .first()
                    )
                elif selected_section == "D1D4":
                    meter_total = (
                        db.session.query(D14Reading.total)
                        .filter_by(session_id=closing_session.id)
                        .order_by(D14Reading.id.desc())
                        .first()
                    )
                else:
                    meter_total = None

                meter_total_value = (
                    meter_total[0] if meter_total and meter_total[0] else Decimal(0)
                )

                # ✅ FIXED CALCULATION
                cash_to_bank = meter_total_value - total_credit + total_collection
                grand_total = meter_total_value

                credit_transaction = CreditTransaction(
                    session_id=closing_session.id,
                    gcb=gcb,
                    momo=momo,
                    tingg=tingg,
                    zenith=zenith,
                    republic=republic,
                    prudential=prudential,
                    adb=adb,
                    stanbic=stanbic,
                    ecobank=ecobank,
                    fidelity=fidelity,
                    credit_ab=credit_ab,
                    credit_cf=credit_cf,
                    credit_wl=credit_wl,
                    credit_zl=credit_zl,
                    credit_gc=credit_gc,
                    soc_staff_credit=soc_staff_credit,
                    water_bill=water_bill,
                    ecg_bill=ecg_bill,
                    genset=genset,
                    approve_miscellaneous=approve_miscellaneous,
                    collection_wl=collection_wl,
                    collection_zl=collection_zl,
                    collection_gc=collection_gc,
                    collection_ab=collection_ab,
                    collection_cv=collection_cv,
                    lube_1_liter=lube_1_liter,
                    lube_drum=lube_drum,
                    duster_collection=duster_collection,
                    total_collection=total_collection,
                    total_credit=total_credit,
                    cash_to_bank=cash_to_bank,
                    grand_total=grand_total,
                )

                db.session.add(credit_transaction)
                db.session.commit()

                flash(
                    message=f"Electronic & Credit transactions saved for {selected_section}!",
                    category="success",
                )
            except Exception as e:
                db.session.rollback()
                flash(
                    message=f"Error saving credit transaction: {str(e)}",
                    category="error",
                )

            return redirect(url_for(endpoint="super_admin_secure.secure_adashboard"))

        # ----------- DENOMINATIONS -----------------
        elif "submit_denomination" in request.form:
            try:
                selected_section = request.form.get("selected_section", "S1S2")
                is_reconciliation = selected_section == "reconciliation"

                # 🔹 Step 1: Handle Adjustment Mode
                if is_reconciliation:
                    # Create a temporary adjustment session (not linked to any real section)
                    closing_session = ClosingSession(
                        section="RECONCILIATION",
                        admin_user_name=current_user.username,
                        session_date=date.today(),
                    )
                    db.session.add(closing_session)
                    db.session.flush()  # Get its ID before committing

                # 🔹 Step 2: Handle Normal Mode
                else:
                    closing_session = get_session_for_section(
                        section=selected_section,
                        username=current_user.username,
                        create_if_missing=False,
                    )

                    # Ensure a session exists before proceeding
                    if not closing_session:
                        flash(
                            message="You must first submit a meter reading before denominations!",
                            category="error",
                        )
                        return redirect(url_for("super_admin_secure.secure_adashboard"))

                    # Prevent duplicate denominations for same session
                    existing_paper = PaperTransaction.query.filter_by(
                        session_id=closing_session.id
                    ).first()
                    existing_coins = CoinsTransaction.query.filter_by(
                        session_id=closing_session.id
                    ).first()

                    if existing_paper or existing_coins:
                        flash(
                            message="Denominations already submitted for this session!",
                            category="error",
                        )
                        return redirect(url_for("super_admin_secure.secure_adashboard"))

                # 🔹 Step 3: Save Denominations
                saved_any = False

                # ---------- PAPER ----------
                if paper_form.validate_on_submit():
                    paper_tx = PaperTransaction(
                        session_id=closing_session.id,
                        note_200=paper_form.note_200.data or 0,
                        note_100=paper_form.note_100.data or 0,
                        note_50=paper_form.note_50.data or 0,
                        note_20=paper_form.note_20.data or 0,
                        note_10=paper_form.note_10.data or 0,
                        note_5=paper_form.note_5.data or 0,
                        note_2=paper_form.note_2.data or 0,
                        note_1=paper_form.note_1.data or 0,
                        is_reconciliation=is_reconciliation,
                    )
                    db.session.add(paper_tx)
                    saved_any = True

                # ---------- COINS ----------
                if coins_form.validate_on_submit():
                    coin_tx = CoinsTransaction(
                        session_id=closing_session.id,
                        coin_5=coins_form.coin_5.data or 0,
                        coin_2=coins_form.coin_2.data or 0,
                        coin_1=coins_form.coin_1.data or 0,
                        is_reconciliation=is_reconciliation,
                    )
                    db.session.add(coin_tx)
                    saved_any = True

                # 🔹 Step 4: Commit and Notify
                if saved_any:
                    db.session.commit()
                    msg_type = "Adjustment" if is_reconciliation else selected_section
                    flash(
                        message=f"Denomination(s) saved successfully for {msg_type}",
                        category="success",
                    )
                else:
                    flash(message="No denomination data provided", category="error")

            except Exception as e:
                db.session.rollback()
                flash(message=f"Error saving denominations: {str(e)}", category="error")

            return redirect(url_for("super_admin_secure.secure_adashboard"))

    return render_template(
        "layout.html",
        d1d4_form=d1d4_form,
        s1s2_form=s1s2_form,
        s3s4_form=s3s4_form,
        paper_form=paper_form,
        coins_form=coins_form,
        credit_form=credit_form,
        sessions=closing_sessions,
        section_form=section_form,
        per_page_form=per_page_form,
    )


@super_admin_secure.route(
    rule="/edit_session/<int:session_id>", methods=["GET", "POST"]
)
@login_required
def edit_session(session_id):
    closing_session = ClosingSession.query.get_or_404(ident=session_id)

    credit_tx = (
        closing_session.credit_transactions[0]
        if closing_session.credit_transactions
        else None
    )
    paper_tx = (
        closing_session.paper_transactions[0]
        if closing_session.paper_transactions
        else None
    )
    coins_tx = (
        closing_session.coin_transactions[0]
        if closing_session.coin_transactions
        else None
    )

    # Build forms with existing objects
    credit_form = CreditTransactionForm(obj=credit_tx)
    paper_form = PaperDinominationForm(obj=paper_tx)
    coins_form = CoinsDinominationForm(obj=coins_tx)

    # SECTION dropdowns: prefill with the session's current section so the hidden field has a value
    section_form = SectionForm()
    denom_section_form = SectionForm()
    # important: set select default so template shows the right item and hidden field has a good value
    section_form.section.data = closing_session.section
    denom_section_form.section.data = closing_session.section

    if request.method == "POST":
        # prefer validate_on_submit semantics — but we already check POST above
        if credit_form.validate() and paper_form.validate() and coins_form.validate():
            try:
                # READ selected_section robustly (handle empty string)
                selected_section = (
                    request.form.get("selected_section")
                    or closing_session.section
                    or "S1S2"
                )

                # Read numeric inputs (safe fallback to Decimal(0))
                def D(v):
                    try:
                        return (
                            v
                            if isinstance(v, Decimal)
                            else Decimal(str(v)) if v not in (None, "") else Decimal(0)
                        )
                    except Exception:
                        return Decimal(0)

                gcb = D(credit_form.gcb.data)
                momo = D(credit_form.momo.data)
                tingg = D(credit_form.tingg.data)
                zenith = D(credit_form.zenith.data)

                # New banks 🏦
                republic = D(credit_form.republic.data)
                prudential = D(credit_form.prudential.data)
                adb = D(credit_form.adb.data)
                stanbic = D(credit_form.stanbic.data)
                ecobank = D(credit_form.ecobank.data)
                fidelity = D(credit_form.fidelity.data)

                credit_ab = D(credit_form.credit_ab.data)
                credit_cf = D(credit_form.credit_cf.data)
                credit_gc = D(credit_form.credit_gc.data)
                credit_wl = D(credit_form.credit_wl.data)
                credit_zl = D(credit_form.credit_zl.data)
                soc_staff_credit = D(credit_form.soc_staff_credit.data)

                # New deductions 🧾
                water_bill = D(credit_form.water_bill.data)
                ecg_bill = D(credit_form.ecg_bill.data)
                genset = D(credit_form.genset.data)
                approve_miscellaneous = D(credit_form.approve_miscellaneous.data)

                collection_ab = D(credit_form.collection_ab.data)
                collection_wl = D(credit_form.collection_wl.data)
                collection_zl = D(credit_form.collection_zl.data)
                collection_gc = D(credit_form.collection_gc.data)
                collection_cv = D(credit_form.collection_cv.data)
                lube_1_liter = D(credit_form.lube_1_liter.data)
                lube_drum = D(credit_form.lube_drum.data)
                duster_collection = D(credit_form.duster_collection.data)

                total_credit = sum(
                    [
                        gcb,
                        momo,
                        tingg,
                        zenith,
                        republic,
                        prudential,
                        adb,
                        stanbic,
                        ecobank,
                        fidelity,
                        credit_ab,
                        credit_cf,
                        credit_gc,
                        credit_wl,
                        credit_zl,
                        soc_staff_credit,
                        water_bill,
                        ecg_bill,
                        genset,
                        approve_miscellaneous,
                    ]
                )

                total_collection = sum(
                    [
                        collection_ab,
                        collection_wl,
                        collection_zl,
                        collection_gc,
                        collection_cv,
                        lube_1_liter,
                        lube_drum,
                        duster_collection,
                    ]
                )

                # fetch meter_total the same way as secure_adashboard
                if selected_section in ["S1S2", "S3S4"]:
                    meter_row = (
                        db.session.query(MeterReading.total)
                        .filter_by(session_id=closing_session.id)
                        .order_by(MeterReading.id.desc())
                        .first()
                    )
                elif selected_section == "D1D4":
                    meter_row = (
                        db.session.query(D14Reading.total)
                        .filter_by(session_id=closing_session.id)
                        .order_by(D14Reading.id.desc())
                        .first()
                    )
                else:
                    meter_row = None

                meter_total_value = (
                    meter_row[0] if meter_row and meter_row[0] else Decimal(0)
                )

                # canonical server formula (same as create)
                cash_to_bank = meter_total_value - total_credit + total_collection
                grand_total = meter_total_value

                # create or update credit_tx
                if credit_tx:
                    credit_form.populate_obj(credit_tx)
                else:
                    credit_tx = CreditTransaction()
                    credit_form.populate_obj(credit_tx)
                    closing_session.credit_transactions.append(credit_tx)

                # Override computed totals with server-calc (important)
                credit_tx.total_collection = total_collection
                credit_tx.total_credit = total_credit
                credit_tx.cash_to_bank = cash_to_bank
                credit_tx.grand_total = grand_total

                # paper & coins
                if paper_tx:
                    paper_form.populate_obj(paper_tx)
                else:
                    new_paper = PaperTransaction()
                    paper_form.populate_obj(new_paper)
                    closing_session.paper_transactions.append(new_paper)

                if coins_tx:
                    coins_form.populate_obj(coins_tx)
                else:
                    new_coins = CoinsTransaction()
                    coins_form.populate_obj(new_coins)
                    closing_session.coin_transactions.append(new_coins)

                # debug log (optional, remove in prod)
                current_app.logger.debug(
                    msg=f"EDIT_SESSION: section={selected_section}, meter_total={meter_total_value}, "
                    f"total_credit={total_credit}, total_collection={total_collection}, cash_to_bank={cash_to_bank}"
                )

                db.session.commit()
                flash(message="Session updated successfully ✅", category="success")
                return redirect(
                    url_for(endpoint="super_admin_secure.secure_adashboard")
                )

            except Exception as e:
                db.session.rollback()
                current_app.logger.exception(msg="Error updating session")
                flash(message=f"Error updating session: {e}", category="error")

    # Render: forms are pre-populated via obj=... so fields show existing DB values
    return render_template(
        "edit_session.html",
        session=closing_session,
        credit_form=credit_form,
        paper_form=paper_form,
        coins_form=coins_form,
        section_form=section_form,
        denom_section_form=denom_section_form,
    )


@super_admin_secure.route("/firebase-messaging-sw.js")
def firebase_messaging_sw():
    return (
        "/* Firebase service worker placeholder */",
        200,
        {"Content-Type": "application/javascript"},
    )


@super_admin_secure.route(rule="/account_mgr/admin/logout")
def super_admin_logout():
    logout_user()
    flash(message="Logout Successfully", category="success")
    return redirect(url_for(endpoint="super_admin_secure.secure_superlogin"))
