from flask import Blueprint, render_template, request, jsonify, current_app
from app import db
# from app.models import Household, Parent  # adjust import path if needed
from app.models import Household, Parent, Child, ChildContract, ChildMedicalInfo, ChildEmergencyContact, ChildParentRelationship, Branch, Room, Educator, EducatorRoom, EducatorWorkingHour, EducatorAttendance, AttendanceSession, ChildRoom, ChildAttendance, ChildAttendanceHistory

household_bp = Blueprint("household", __name__)

# -----------------------------------------------------------
# PAGE VIEW
# -----------------------------------------------------------
@household_bp.route("/household")
def household():
    """Render Household Management page."""
    return render_template("registration/household/household.html")


@household_bp.route("/debug-db")
def debug_db():
    import os
    return os.getenv("DATABASE_URL")


# -----------------------------------------------------------
# CREATE / UPDATE HOUSEHOLD + PARENTS  (SQLAlchemy ORM)
# -----------------------------------------------------------
@household_bp.route("/api/household", methods=["POST"])
def save_household():
    data = request.get_json() or {}

    if not data.get("household_name"):
        return jsonify({"success": False, "error": "Household name is required"}), 400

    try:
        household_id = data.get("household_id")

        # --- UPSERT HOUSEHOLD ---
        if household_id:
            household = Household.query.get(household_id)
            if not household:
                return jsonify({"success": False, "error": "Household not found"}), 404
        else:
            household = Household()
            db.session.add(household)

        # Set household fields
        household.household_name = data.get("household_name")
        household.address_line1 = data.get("address_line1")
        household.address_line2 = data.get("address_line2")
        household.city = data.get("city")
        household.county = data.get("county")
        household.eircode = data.get("eircode")
        household.phone = data.get("phone")

        # Flush so new household gets an ID before using it for parents
        db.session.flush()
        household_id = household.household_id

        # --- UPSERT PARENTS ---
        submitted_ids = []

        # Build a dict of existing parents keyed by id for quick access
        existing_parents = {
            p.parent_id: p for p in Parent.query.filter_by(household_id=household_id).all()
        }

        for p_data in data.get("parents", []):
            parent_id = p_data.get("parent_id")

            if parent_id:
                parent = existing_parents.get(parent_id)
                if not parent:
                    # If a parent_id is sent that doesn't belong to this household, skip or raise
                    # Here we'll just skip to avoid inconsistent client data
                    continue
            else:
                parent = Parent(household_id=household_id)
                db.session.add(parent)

            parent.first_name = p_data.get("first_name")
            parent.last_name = p_data.get("last_name")
            parent.phone = p_data.get("phone")
            parent.email = p_data.get("email")
            parent.is_primary = bool(p_data.get("is_primary"))

            # Ensure we have an ID after flush (for new parents)
            db.session.flush()
            submitted_ids.append(parent.parent_id)

        # --- DELETE REMOVED PARENTS ---
        if submitted_ids:
            (
                Parent.query
                .filter(
                    Parent.household_id == household_id,
                    ~Parent.parent_id.in_(submitted_ids)
                )
                .delete(synchronize_session=False)
            )
        else:
            Parent.query.filter_by(household_id=household_id).delete(synchronize_session=False)

        db.session.commit()

        return jsonify({
            "success": True,
            "household_id": household_id,
            "message": "Household saved successfully"
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Household save failed")
        return jsonify({"success": False, "error": str(e)}), 500


# -----------------------------------------------------------
# FETCH ALL HOUSEHOLDS (FOR DROPDOWN)
# -----------------------------------------------------------
@household_bp.route("/api/households")
def get_households():
    try:
        households = Household.query.order_by(Household.household_name).all()
        result = [
            {
                "household_id": h.household_id,
                "household_name": h.household_name
            }
            for h in households
        ]
        return jsonify(result)
    except Exception as e:
            current_app.logger.exception("Error fetching households")
            return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------
# GET SINGLE HOUSEHOLD (+ PARENTS)
# -----------------------------------------------------------
@household_bp.route("/api/household/<int:household_id>")
def get_household(household_id):
    household = Household.query.get(household_id)
    if not household:
        return jsonify({"error": "Household not found"}), 404

    parents = (
        Parent.query
        .filter_by(household_id=household_id)
        .order_by(Parent.is_primary.desc(), Parent.parent_id.asc())
        .all()
    )

    household_dict = {
        "household_id": household.household_id,
        "household_name": household.household_name,
        "address_line1": household.address_line1,
        "address_line2": household.address_line2,
        "city": household.city,
        "county": household.county,
        "eircode": household.eircode,
        "phone": household.phone,
    }

    parents_list = [
        {
            "parent_id": p.parent_id,
            "household_id": p.household_id,
            "first_name": p.first_name,
            "last_name": p.last_name,
            "phone": p.phone,
            "email": p.email,
            "is_primary": bool(p.is_primary),
        }
        for p in parents
    ]

    return jsonify({
        "household": household_dict,
        "parents": parents_list,
    })
