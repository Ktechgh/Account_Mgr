from account_mgr import db
from .form import AttendantForm
from flask_login import login_required
from account_mgr.database.models import CSAName
from flask import render_template, url_for, flash, redirect, Blueprint


attendants_registration = Blueprint(
    import_name=__name__,
    name="attendants_registration",
    template_folder="templates",
    static_folder="static",
)


@attendants_registration.route(rule="/account_mgr/add_attendant", methods=["GET", "POST"])
@login_required
def add_attendant():
    csa_form = AttendantForm()

    if csa_form.validate_on_submit():
        # Normalize name (remove spaces + make case-insensitive)
        new_name = csa_form.attendant_name.data.strip().title()

        # Check if attendant already exists
        existing = CSAName.query.filter(
            db.func.lower(CSAName.attendant_name) == new_name.lower()
        ).first()

        if existing:
            flash(message=f"CSA '{new_name}' already exists!", category="error")
        else:
            new_attendant = CSAName(attendant_name=new_name)
            db.session.add(new_attendant)
            db.session.commit()
            flash(message="Attendant added successfully", category="success")
            return redirect(url_for(endpoint="attendants_registration.add_attendant"))

    attendants = CSAName.query.all()
    return render_template(
        "add_attendant_.html", csa_form=csa_form, attendants=attendants
    )


@attendants_registration.route(
    rule="/account_mgr/update_attendant/<int:attendant_id>", methods=["GET", "POST"]
)
@login_required
def update_attendant(attendant_id):
    attendant = CSAName.query.get_or_404(attendant_id)
    csa_form = AttendantForm(obj=attendant)

    if csa_form.validate_on_submit():
        new_name = csa_form.attendant_name.data.strip().title()

        # Check for duplicates excluding current record
        existing = CSAName.query.filter(
            db.func.lower(CSAName.attendant_name) == new_name.lower(),
            CSAName.id != attendant.id,
        ).first()

        if existing:
            flash(message=f"CSA '{new_name}' already exists!", category="error")
        else:
            attendant.attendant_name = new_name
            try:
                db.session.commit()
                flash(message="Attendant updated successfully", category="success")
                return redirect(
                    url_for(endpoint="super_admin_secure.secure_adashboard")
                )
            except Exception:
                db.session.rollback()
                flash(message=f"Error updating attendant", category="error")

    return render_template(
        "update_attendant.html", csa_form=csa_form, attendant=attendant
    )


@attendants_registration.route(rule="/account_mgr/delete_attendant/<int:attendant_id>")
@login_required
def delete_attendant(attendant_id):
    attendant = CSAName.query.get_or_404(attendant_id)
    try:
        db.session.delete(attendant)
        db.session.commit()
        flash(message="Attendant deleted successfully", category="success")
    except Exception as e:
        db.session.rollback()
        flash(message=f"Error deleting attendant: {str(e)}", category="error")

    return redirect(url_for(endpoint="super_admin_secure.secure_adashboard"))
