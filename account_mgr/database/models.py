from datetime import date
from sqlalchemy import DateTime
from sqlalchemy.sql import func
from flask_login import UserMixin
from sqlalchemy.orm import validates
from decimal import Decimal, ROUND_HALF_UP
from account_mgr import db, login_manager, app
from itsdangerous import URLSafeTimedSerializer


@login_manager.user_loader
def load_user(user_id):
    """Load user from the database using the user ID."""
    return User.query.get(int(user_id))


class Tenant(db.Model):
    """Model for storing tenant information."""

    __tablename__ = "tenants"

    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(150), nullable=False)
    shop_code = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)

    users = db.relationship("User", back_populates="tenant", lazy=True)

    def __repr__(self):
        return f"<Tenant {self.shop_code} - {self.business_name}>"


class User(db.Model, UserMixin):
    """Model for storing user information."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, unique=True)
    email = db.Column(db.String(length=255), unique=True, nullable=True)
    username = db.Column(db.String(length=150), nullable=True)
    staff_id = db.Column(db.String(length=100), unique=True, nullable=False)
    password = db.Column(db.String(length=255), nullable=False)
    user_role = db.Column(db.String(length=100), nullable=False)
    is_super_admin = db.Column(db.Boolean, default=False)
    is_default_credential = db.Column(db.Boolean, default=True)
    user_profile = db.Column(
        db.String(length=200), nullable=False, default="default.jpg"
    )
    date_created = db.Column(db.DateTime, default=func.now(), nullable=False)

    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    tenant = db.relationship("Tenant", back_populates="users")

    __table_args__ = (db.Index("user_idx", "date_created"),)

    def __repr__(self) -> str:
        return f"User('{self.username}')"

    def get_reset_token(self):
        """Generate a password reset token for the user."""
        s = URLSafeTimedSerializer(app.config["SECRET_KEY"])
        return s.dumps({"user_id": self.id})

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        """Verify the password reset token."""
        s = URLSafeTimedSerializer(app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token, max_age=expires_sec)["user_id"]
        except Exception:
            return None
        return User.query.get(user_id)


class ClosingSession(db.Model):
    """Model for storing closing session information."""

    __tablename__ = "closing_sessions"

    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.String(100), nullable=False)
    admin_user_name = db.Column(db.String(100), nullable=True)

    # New explicit session_date column
    session_date = db.Column(db.Date, nullable=False, default=date.today, index=True)

    # Relationships with cascade delete
    credit_transactions = db.relationship(
        "CreditTransaction", backref="session", lazy=True, cascade="all, delete-orphan"
    )
    paper_transactions = db.relationship(
        "PaperTransaction", backref="session", lazy=True, cascade="all, delete-orphan"
    )
    coin_transactions = db.relationship(
        "CoinsTransaction", backref="session", lazy=True, cascade="all, delete-orphan"
    )
    meter_readings = db.relationship(
        "MeterReading", backref="session", lazy=True, cascade="all, delete-orphan"
    )
    d14_readings = db.relationship(
        "D14Reading", backref="session", lazy=True, cascade="all, delete-orphan"
    )

    date_created = db.Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self):
        return f"<ClosingSession {self.section} - {self.session_date}>"


# ---------------- METER READINGS ----------------
class MeterReading(db.Model):
    """Model for storing meter readings."""

    __tablename__ = "meter_readings"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(
        db.Integer, db.ForeignKey("closing_sessions.id"), nullable=False
    )

    section = db.Column(db.String(10), nullable=False, index=True)
    super_1_opening = db.Column(db.Numeric(12, 2), nullable=False)
    super_2_opening = db.Column(db.Numeric(12, 2), nullable=False)
    super_1_closing = db.Column(db.Numeric(12, 2), nullable=False)
    super_2_closing = db.Column(db.Numeric(12, 2), nullable=False)
    liters_sold = db.Column(db.Numeric(12, 2), nullable=False)
    gsa_test_draw = db.Column(db.Numeric(12, 2), nullable=True)
    price = db.Column(db.Numeric(12, 2), nullable=False)
    total = db.Column(db.Numeric(12, 2), nullable=False)
    date_of_sale = db.Column(db.Date, nullable=False)
    date_created = db.Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    csa_name = db.Column(db.String(length=100), nullable=False)

    def __repr__(self):
        return f"<MeterReading {self.liters_sold}L - {self.price}>"


# ---------------- DIESEL READINGS (D1-D4) ----------------
class D14Reading(db.Model):
    """Model for storing diesel meter readings (D1-D4)."""

    __tablename__ = "d14_readings"

    id = db.Column(db.Integer, primary_key=True)

    session_id = db.Column(
        db.Integer, db.ForeignKey("closing_sessions.id"), nullable=False
    )

    section = db.Column(db.String(100), nullable=False, index=True)

    d1_opening = db.Column(db.Numeric(12, 2), nullable=False)
    d1_closing = db.Column(db.Numeric(12, 2), nullable=False)
    d2_opening = db.Column(db.Numeric(12, 2), nullable=False)
    d2_closing = db.Column(db.Numeric(12, 2), nullable=False)
    d3_opening = db.Column(db.Numeric(12, 2), nullable=False)
    d3_closing = db.Column(db.Numeric(12, 2), nullable=False)
    d4_opening = db.Column(db.Numeric(12, 2), nullable=False)
    d4_closing = db.Column(db.Numeric(12, 2), nullable=False)
    rtt_liters = db.Column(db.Numeric(12, 2), nullable=True)
    liters_sold = db.Column(db.Numeric(12, 2), nullable=False)
    price = db.Column(db.Numeric(12, 2), nullable=False)
    total = db.Column(db.Numeric(12, 2), nullable=False)
    date_of_sale = db.Column(db.Date, nullable=False)
    date_created = db.Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    csa_name = db.Column(db.String(length=100), nullable=False)

    def __repr__(self):
        return f"<D14Reading {self.section} - {self.liters_sold}L>"


# ---------------- CREDIT / E-TRANSACTIONS ----------------
class CreditTransaction(db.Model):
    """Model for storing credit transactions."""

    __tablename__ = "credit_transactions"

    __table_args__ = (
        db.UniqueConstraint("session_id", name="unique_credit_per_session"),
    )

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(
        db.Integer, db.ForeignKey("closing_sessions.id"), nullable=False
    )

    # Electronic & Credit Transactions
    gcb = db.Column(db.Numeric(12, 2), nullable=True)
    momo = db.Column(db.Numeric(12, 2), nullable=True)
    tingg = db.Column(db.Numeric(12, 2), nullable=True)
    zenith = db.Column(db.Numeric(12, 2), nullable=True)

    republic = db.Column(db.Numeric(12, 2), nullable=True)
    prudential = db.Column(db.Numeric(12, 2), nullable=True)
    adb = db.Column(db.Numeric(12, 2), nullable=True)
    stanbic = db.Column(db.Numeric(12, 2), nullable=True)
    ecobank = db.Column(db.Numeric(12, 2), nullable=True)
    fidelity = db.Column(db.Numeric(12, 2), nullable=True)

    credit_ab = db.Column(db.Numeric(12, 2), nullable=True)
    credit_cf = db.Column(db.Numeric(12, 2), nullable=True)
    credit_gc = db.Column(db.Numeric(12, 2), nullable=True)
    credit_wl = db.Column(db.Numeric(12, 2), nullable=True)
    credit_zl = db.Column(db.Numeric(12, 2), nullable=True)
    soc_staff_credit = db.Column(db.Numeric(12, 2), nullable=True)

    # 💧 New DD Fields (deductions moved to credit section)
    water_bill = db.Column(db.Numeric(12, 2), nullable=True)
    ecg_bill = db.Column(db.Numeric(12, 2), nullable=True)
    genset = db.Column(db.Numeric(12, 2), nullable=True)
    approve_miscellaneous = db.Column(db.Numeric(12, 2), nullable=True)

    # Collections
    collection_ab = db.Column(db.Numeric(12, 2), nullable=True)
    collection_wl = db.Column(db.Numeric(12, 2), nullable=True)
    collection_zl = db.Column(db.Numeric(12, 2), nullable=True)
    collection_gc = db.Column(db.Numeric(12, 2), nullable=True)
    collection_cv = db.Column(db.Numeric(12, 2), nullable=True)

    # Other Sales
    lube_1_liter = db.Column(db.Numeric(12, 2), nullable=True)
    lube_drum = db.Column(db.Numeric(12, 2), nullable=True)
    duster_collection = db.Column(db.Numeric(12, 2), nullable=True)

    # Totals
    total_collection = db.Column(db.Numeric(12, 2), nullable=True)
    total_credit = db.Column(db.Numeric(12, 2), nullable=True)
    cash_to_bank = db.Column(db.Numeric(12, 2), nullable=True)
    grand_total = db.Column(db.Numeric(12, 2), nullable=True)

    date_created = db.Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    @validates("cash_to_bank")
    def round_cash_to_bank(self, key, value):
        if value is not None:
            return Decimal(value).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        return value


# ---------------- PAPER CASH ----------------
class PaperTransaction(db.Model):
    """Model for storing paper cash transactions."""

    __tablename__ = "paper_transactions"

    __table_args__ = (
        db.UniqueConstraint("session_id", name="unique_paper_per_session"),
    )

    id = db.Column(db.Integer, primary_key=True)

    session_id = db.Column(
        db.Integer, db.ForeignKey("closing_sessions.id"), nullable=False
    )

    note_200 = db.Column(db.Integer, nullable=True)
    note_100 = db.Column(db.Integer, nullable=True)
    note_50 = db.Column(db.Integer, nullable=True)
    note_20 = db.Column(db.Integer, nullable=True)
    note_10 = db.Column(db.Integer, nullable=True)
    note_5 = db.Column(db.Integer, nullable=True)
    note_2 = db.Column(db.Integer, nullable=True)
    note_1 = db.Column(db.Integer, nullable=True)
    date_created = db.Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    is_reconciliation = db.Column(db.Boolean, default=False)


# ---------------- COINS ----------------
class CoinsTransaction(db.Model):
    """Model for storing coins transactions."""

    __tablename__ = "coins_transactions"

    __table_args__ = (
        db.UniqueConstraint("session_id", name="unique_coins_per_session"),
    )

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(
        db.Integer, db.ForeignKey("closing_sessions.id"), nullable=False
    )
    coin_5 = db.Column(db.Integer, nullable=True)
    coin_2 = db.Column(db.Integer, nullable=True)
    coin_1 = db.Column(db.Integer, nullable=True)
    date_created = db.Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    is_reconciliation = db.Column(db.Boolean, default=False)


class CSAName(db.Model):
    """Model for storing CSA names (master list of attendants)"""

    __tablename__ = "csanames"

    id = db.Column(db.Integer, primary_key=True)
    attendant_name = db.Column(db.String(length=100), nullable=False, unique=True)

    def __repr__(self):
        return f"<CSAName {self.attendant_name}>"


class DailyReport(db.Model):
    __tablename__ = "daily_reports"

    id = db.Column(db.Integer, primary_key=True)
    report_title = db.Column(db.String(100), nullable=False)
    report_body = db.Column(db.String(100), nullable=False)

    def __repr__(self) -> str:
        return f"User('{self.report_title}', '{self.report_body}')"
