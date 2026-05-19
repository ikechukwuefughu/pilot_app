from flask import Blueprint, render_template, request, jsonify
from app.config import get_db_connection
from datetime import date

children_bp = Blueprint(
    "children",
    __name__,
    url_prefix="/children"
)

# ==========================================================
# PAGE
# ==========================================================
@children_bp.route("/")
def child_setup():
    return render_template("registration/children/child.html")


# ==========================================================
# SAVE (CREATE + UPDATE)
# ==========================================================
@children_bp.route("/api/child/setup", methods=["POST"])
def save_children():

    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        household_id = data.get("household_id")
        children = data.get("children", [])

        if not household_id:
            return jsonify({"success": False, "error": "household_id required"}), 400

        submitted_child_ids = set()

        for c in children:

            child_id = c.get("child_id")
            contract = c.get("contract", {})

            # ================= STATUS =================
            status = "Active"
            if contract.get("end_date"):
                try:
                    if date.fromisoformat(contract["end_date"]) < date.today():
                        status = "Inactive"
                except:
                    pass

            # ================= CHILD UPSERT =================
            if child_id:

                submitted_child_ids.add(int(child_id))

                cursor.execute("""
                    UPDATE child
                    SET household_id = ?,
                        first_name = ?,
                        last_name = ?,
                        date_of_birth = ?,
                        ppsn = ?,
                        chick_code = ?,
                        ecce_eligible = ?,
                        start_date = ?
                    WHERE child_id = ?
                """, (
                    household_id,
                    c.get("first_name"),
                    c.get("last_name"),
                    c.get("date_of_birth"),
                    c.get("ppsn"),
                    c.get("chick_code"),
                    1 if c.get("ecce_eligible") else 0,
                    c.get("start_date"),
                    child_id
                ))

            else:

                cursor.execute("""
                    INSERT INTO child (
                        household_id,
                        first_name,
                        last_name,
                        date_of_birth,
                        ppsn,
                        chick_code,
                        ecce_eligible,
                        start_date
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    household_id,
                    c.get("first_name"),
                    c.get("last_name"),
                    c.get("date_of_birth"),
                    c.get("ppsn"),
                    c.get("chick_code"),
                    1 if c.get("ecce_eligible") else 0,
                    c.get("start_date")
                ))

                child_id = cursor.lastrowid
                submitted_child_ids.add(child_id)

            # ================= CONTRACT UPSERT =================
            contract_id = contract.get("contract_id")

            if contract_id:

                cursor.execute("""
                    UPDATE child_contracts
                    SET contract_type = ?,
                        start_date = ?,
                        end_date = ?,
                        agreed_hours_per_week = ?,
                        hourly_rate = ?,
                        subsidy_rate = ?,
                        status = ?
                    WHERE contract_id = ?
                """, (
                    contract.get("type"),
                    contract.get("start_date"),
                    contract.get("end_date"),
                    contract.get("hours_per_week"),
                    contract.get("hourly_rate"),
                    contract.get("subsidy_rate"),
                    status,
                    contract_id
                ))

            else:

                cursor.execute("""
                    INSERT INTO child_contracts (
                        child_id,
                        contract_type,
                        start_date,
                        end_date,
                        agreed_hours_per_week,
                        hourly_rate,
                        subsidy_rate,
                        status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    child_id,
                    contract.get("type"),
                    contract.get("start_date"),
                    contract.get("end_date"),
                    contract.get("hours_per_week"),
                    contract.get("hourly_rate"),
                    contract.get("subsidy_rate"),
                    status
                ))

        conn.commit()

        return jsonify({"success": True, "message": "Saved successfully"})

    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

    finally:
        conn.close()


# ==========================================================
# HOUSEHOLDS
# ==========================================================
@children_bp.route("/api/households", methods=["GET"])
def get_households():

    conn = get_db_connection()

    rows = conn.execute("""
        SELECT household_id, household_name
        FROM household
        ORDER BY household_name
    """).fetchall()

    conn.close()

    return jsonify([dict(r) for r in rows])


# ==========================================================
# EDIT MODE DATA LOADER (KEY PIECE)
# ==========================================================
@children_bp.route("/api/household/<int:household_id>", methods=["GET"])
def get_household(household_id):

    conn = get_db_connection()

    household = conn.execute("""
        SELECT * FROM household WHERE household_id = ?
    """, (household_id,)).fetchone()

    parents = conn.execute("""
        SELECT * FROM parent WHERE household_id = ?
    """, (household_id,)).fetchall()

    rows = conn.execute("""
        SELECT 
            c.child_id,
            c.first_name,
            c.last_name,
            c.date_of_birth,
            c.ppsn,
            c.chick_code,
            c.ecce_eligible,
            c.start_date,

            cc.contract_id,
            cc.contract_type,
            cc.start_date AS contract_start_date,
            cc.end_date,
            cc.agreed_hours_per_week,
            cc.hourly_rate,
            cc.subsidy_rate

        FROM child c
        LEFT JOIN child_contracts cc ON cc.child_id = c.child_id
        WHERE c.household_id = ?
    """, (household_id,)).fetchall()

    conn.close()

    return jsonify({
        "household": dict(household),
        "parents": [dict(p) for p in parents],
        "children": [dict(r) for r in rows]
    })