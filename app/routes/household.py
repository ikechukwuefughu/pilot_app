from flask import Blueprint, render_template, request, jsonify, current_app
from app.config import get_db_connection

household_bp = Blueprint("household", __name__)

# -----------------------------------------------------------
# PAGE VIEW
# -----------------------------------------------------------
@household_bp.route("/household")
def household():
    """Render Household Management page."""
    return render_template("registration/household/household.html")


# -----------------------------------------------------------
# CREATE / UPDATE HOUSEHOLD + PARENTS
# -----------------------------------------------------------
@household_bp.route("/api/household", methods=["POST"])
def save_household():
    data = request.get_json() or {}
    conn = get_db_connection()
    cursor = conn.cursor()

    if not data.get("household_name"):
        return jsonify({"success": False, "error": "Household name is required"}), 400

    try:
        household_id = data.get("household_id")

        # --- UPSERT HOUSEHOLD ---
        if household_id:
            cursor.execute("""
                UPDATE household
                SET household_name = ?, address_line1 = ?, address_line2 = ?,
                    city = ?, county = ?, eircode = ?, phone = ?
                WHERE household_id = ?
            """, (
                data.get("household_name"), data.get("address_line1"),
                data.get("address_line2"), data.get("city"), data.get("county"),
                data.get("eircode"), data.get("phone"), household_id
            ))
        else:
            cursor.execute("""
                INSERT INTO household (household_name, address_line1, address_line2,
                    city, county, eircode, phone)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get("household_name"), data.get("address_line1"),
                data.get("address_line2"), data.get("city"), data.get("county"),
                data.get("eircode"), data.get("phone")
            ))
            household_id = cursor.lastrowid

        # --- UPSERT PARENTS ---
        submitted_ids = []
        for p in data.get("parents", []):
            parent_id = p.get("parent_id")
            fields = (p.get("first_name"), p.get("last_name"),
                      p.get("phone"), p.get("email"),
                      1 if p.get("is_primary") else 0)
            if parent_id:
                submitted_ids.append(parent_id)
                cursor.execute("""
                    UPDATE parent
                    SET first_name=?, last_name=?, phone=?, email=?, is_primary=?
                    WHERE parent_id=? AND household_id=?
                """, (*fields, parent_id, household_id))
            else:
                cursor.execute("""
                    INSERT INTO parent (household_id, first_name, last_name, phone, email, is_primary)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (household_id, *fields))
                submitted_ids.append(cursor.lastrowid)

        # --- DELETE REMOVED PARENTS ---
        if submitted_ids:
            placeholders = ",".join("?" for _ in submitted_ids)
            cursor.execute(
                f"DELETE FROM parent WHERE household_id=? AND parent_id NOT IN ({placeholders})",
                [household_id, *submitted_ids]
            )
        else:
            cursor.execute("DELETE FROM parent WHERE household_id=?", (household_id,))

        conn.commit()
        return jsonify({
            "success": True,
            "household_id": household_id,
            "message": "Household saved successfully"
        })

    except Exception as e:
        conn.rollback()
        current_app.logger.exception("Household save failed")
        return jsonify({"success": False, "error": "Unable to save household."}), 500
    finally:
        conn.close()


# -----------------------------------------------------------
# FETCH ALL HOUSEHOLDS (FOR DROPDOWN)
# -----------------------------------------------------------
@household_bp.route("/api/households")
def get_households():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT household_id, household_name
        FROM household
        ORDER BY household_name
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# -----------------------------------------------------------
# GET SINGLE HOUSEHOLD (+ PARENTS)
# -----------------------------------------------------------
@household_bp.route("/api/household/<int:household_id>")
def get_household(household_id):
    conn = get_db_connection()
    household = conn.execute("SELECT * FROM household WHERE household_id = ?", (household_id,)).fetchone()
    if not household:
        conn.close()
        return jsonify({"error": "Household not found"}), 404

    parents = conn.execute("""
        SELECT * FROM parent
        WHERE household_id = ?
        ORDER BY is_primary DESC, parent_id
    """, (household_id,)).fetchall()
    conn.close()

    return jsonify({
        "household": dict(household),
        "parents": [dict(p) for p in parents]
    })

# from flask import Blueprint, render_template, request, jsonify
# from app.config import get_db_connection

# household_bp = Blueprint("household", __name__)


# @household_bp.route("/household")
# def household():
#     return render_template("household/household.html")


# @household_bp.route("/api/household", methods=["POST"])
# def save_household():
#     data = request.get_json()

#     conn = get_db_connection()
#     cursor = conn.cursor()

#     try:
#         household_id = data.get("household_id")

#         # ======================================================
#         # UPDATE EXISTING HOUSEHOLD
#         # ======================================================
#         if household_id:
#             cursor.execute("""
#                 UPDATE household
#                 SET household_name = ?,
#                     address_line1 = ?,
#                     address_line2 = ?,
#                     city = ?,
#                     county = ?,
#                     eircode = ?,
#                     phone = ?
#                 WHERE household_id = ?
#             """, (
#                 data.get("household_name"),
#                 data.get("address_line1"),
#                 data.get("address_line2"),
#                 data.get("city"),
#                 data.get("county"),
#                 data.get("eircode"),
#                 data.get("phone"),
#                 household_id
#             ))
#         else:
#             cursor.execute("""
#                 INSERT INTO household (
#                     household_name,
#                     address_line1,
#                     address_line2,
#                     city,
#                     county,
#                     eircode,
#                     phone
#                 )
#                 VALUES (?, ?, ?, ?, ?, ?, ?)
#             """, (
#                 data.get("household_name"),
#                 data.get("address_line1"),
#                 data.get("address_line2"),
#                 data.get("city"),
#                 data.get("county"),
#                 data.get("eircode"),
#                 data.get("phone")
#             ))
#             household_id = cursor.lastrowid

#         # ======================================================
#         # UPSERT PARENTS (PRESERVE IDs)
#         # ======================================================
#         submitted_ids = set()

#         for p in data.get("parents", []):
#             parent_id = p.get("parent_id")

#             if parent_id:
#                 submitted_ids.add(int(parent_id))

#                 cursor.execute("""
#                     UPDATE parent
#                     SET first_name = ?,
#                         last_name = ?,
#                         phone = ?,
#                         email = ?,
#                         is_primary = ?
#                     WHERE parent_id = ?
#                 """, (
#                     p.get("first_name"),
#                     p.get("last_name"),
#                     p.get("phone"),
#                     p.get("email"),
#                     1 if p.get("is_primary") else 0,
#                     parent_id
#                 ))
#             else:
#                 cursor.execute("""
#                     INSERT INTO parent (
#                         household_id,
#                         first_name,
#                         last_name,
#                         phone,
#                         email,
#                         is_primary
#                     )
#                     VALUES (?, ?, ?, ?, ?, ?)
#                 """, (
#                     household_id,
#                     p.get("first_name"),
#                     p.get("last_name"),
#                     p.get("phone"),
#                     p.get("email"),
#                     1 if p.get("is_primary") else 0
#                 ))

#                 submitted_ids.add(cursor.lastrowid)

#         # Delete removed parents only
#         if submitted_ids:
#             placeholders = ",".join("?" * len(submitted_ids))
#             cursor.execute(
#                 f"DELETE FROM parent WHERE household_id = ? AND parent_id NOT IN ({placeholders})",
#                 [household_id, *submitted_ids]
#             )
#         else:
#             cursor.execute(
#                 "DELETE FROM parent WHERE household_id = ?",
#                 (household_id,)
#             )

#         conn.commit()

#         return jsonify({
#             "success": True,
#             "household_id": household_id,
#             "message": "Household saved successfully"
#         })

#     except Exception as e:
#         conn.rollback()
#         return jsonify({
#             "success": False,
#             "error": str(e)
#         }), 500

#     finally:
#         conn.close()


# @household_bp.route("/api/households", methods=["GET"])
# def get_households():
#     conn = get_db_connection()

#     rows = conn.execute("""
#         SELECT household_id, household_name
#         FROM household
#         ORDER BY household_name
#     """).fetchall()

#     conn.close()

#     return jsonify([dict(row) for row in rows])


# @household_bp.route("/api/household/<int:household_id>", methods=["GET"])
# def get_household(household_id):
#     conn = get_db_connection()

#     household = conn.execute("""
#         SELECT *
#         FROM household
#         WHERE household_id = ?
#     """, (household_id,)).fetchone()

#     if not household:
#         conn.close()
#         return jsonify({"error": "Household not found"}), 404

#     parents = conn.execute("""
#         SELECT *
#         FROM parent
#         WHERE household_id = ?
#         ORDER BY is_primary DESC, parent_id
#     """, (household_id,)).fetchall()

#     conn.close()

#     return jsonify({
#         "household": dict(household),
#         "parents": [dict(p) for p in parents]
#     })