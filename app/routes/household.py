from flask import Blueprint, render_template, request, jsonify, current_app
from app import db
from app.models import Household, Parent  # adjust import path if needed

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
    households = Household.query.order_by(Household.household_name).all()
    result = [
        {
            "household_id": h.household_id,
            "household_name": h.household_name
        }
        for h in households
    ]
    return jsonify(result)


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

# from flask import Blueprint, render_template, request, jsonify, current_app
# from app.config import get_db_connection
# from app import db

# household_bp = Blueprint("household", __name__)

# # -----------------------------------------------------------
# # PAGE VIEW
# # -----------------------------------------------------------
# @household_bp.route("/household")
# def household():
#     """Render Household Management page."""
#     return render_template("registration/household/household.html")


# @household_bp.route("/debug-db")
# def debug_db():
#     import os
#     return os.getenv("DATABASE_URL")
    
# # -----------------------------------------------------------
# # CREATE / UPDATE HOUSEHOLD + PARENTS
# # -----------------------------------------------------------
# @household_bp.route("/api/household", methods=["POST"])
# def save_household():
#     data = request.get_json() or {}
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     if not data.get("household_name"):
#         return jsonify({"success": False, "error": "Household name is required"}), 400

#     try:
#         household_id = data.get("household_id")

#         # --- UPSERT HOUSEHOLD ---
#         if household_id:
#             cursor.execute("""
#                 UPDATE dbo.household
#                 SET household_name = ?, address_line1 = ?, address_line2 = ?,
#                     city = ?, county = ?, eircode = ?, phone = ?
#                 WHERE household_id = ?
#             """, (
#                 data.get("household_name"), data.get("address_line1"),
#                 data.get("address_line2"), data.get("city"), data.get("county"),
#                 data.get("eircode"), data.get("phone"), household_id
#             ))
#         else:
#             cursor.execute("""
#                 INSERT INTO dbo.household (household_name, address_line1, address_line2,
#                     city, county, eircode, phone)
#                 VALUES (?, ?, ?, ?, ?, ?, ?)
#             """, (
#                 data.get("household_name"), data.get("address_line1"),
#                 data.get("address_line2"), data.get("city"), data.get("county"),
#                 data.get("eircode"), data.get("phone")
#             ))
#             household_id = cursor.lastrowid

#         # --- UPSERT PARENTS ---
#         submitted_ids = []
#         for p in data.get("parents", []):
#             parent_id = p.get("parent_id")
#             fields = (p.get("first_name"), p.get("last_name"),
#                       p.get("phone"), p.get("email"),
#                       1 if p.get("is_primary") else 0)
#             if parent_id:
#                 submitted_ids.append(parent_id)
#                 cursor.execute("""
#                     UPDATE dbo.parent
#                     SET first_name=?, last_name=?, phone=?, email=?, is_primary=?
#                     WHERE parent_id=? AND household_id=?
#                 """, (*fields, parent_id, household_id))
#             else:
#                 cursor.execute("""
#                     INSERT INTO dbo.parent (household_id, first_name, last_name, phone, email, is_primary)
#                     VALUES (?, ?, ?, ?, ?, ?)
#                 """, (household_id, *fields))
#                 submitted_ids.append(cursor.lastrowid)

#         # --- DELETE REMOVED PARENTS ---
#         if submitted_ids:
#             placeholders = ",".join("?" for _ in submitted_ids)
#             cursor.execute(
#                 f"DELETE FROM dbo.parent WHERE household_id=? AND parent_id NOT IN ({placeholders})",
#                 [household_id, *submitted_ids]
#             )
#         else:
#             cursor.execute("DELETE FROM dbo.parent WHERE household_id=?", (household_id,))

#         conn.commit()
#         return jsonify({
#             "success": True,
#             "household_id": household_id,
#             "message": "Household saved successfully"
#         })

#     except Exception as e:
#         conn.rollback()
#         current_app.logger.exception("Household save failed")
#         return jsonify({"success": False, "error": str(e)}), 500
#     finally:
#         conn.close()


# # -----------------------------------------------------------
# # FETCH ALL HOUSEHOLDS (FOR DROPDOWN)
# # -----------------------------------------------------------
# @household_bp.route("/api/households")
# def get_households():
#     conn = get_db_connection()
#     rows = conn.execute("""
#         SELECT household_id, household_name
#         FROM dbo.household
#         ORDER BY household_name
#     """).fetchall()
#     conn.close()
#     return jsonify([dict(r) for r in rows])


# # -----------------------------------------------------------
# # GET SINGLE HOUSEHOLD (+ PARENTS)
# # -----------------------------------------------------------
# @household_bp.route("/api/household/<int:household_id>")
# def get_household(household_id):
#     conn = get_db_connection()
#     household = conn.execute("SELECT * FROM dbo.household WHERE household_id = ?", (household_id,)).fetchone()
#     if not household:
#         conn.close()
#         return jsonify({"error": "Household not found"}), 404

#     parents = conn.execute("""
#         SELECT * FROM dbo.parent
#         WHERE household_id = ?
#         ORDER BY is_primary DESC, parent_id
#     """, (household_id,)).fetchall()
#     conn.close()

#     return jsonify({
#         "household": dict(household),
#         "parents": [dict(p) for p in parents]
#     })
