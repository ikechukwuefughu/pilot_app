"""
Attendance Routes
-----------------
Handles all attendance-related web pages and API endpoints.

Features:
- Displays the attendance page.
- Loads daily attendance records.
- Records child check-in times.
- Records child check-out times.
"""

from flask import Blueprint, render_template, request, jsonify
from app.config import get_db_connection

# Create the Attendance Blueprint
attendance_bp = Blueprint("attendance", __name__)

@attendance_bp.route("/debug/db")
def debug_db():

    conn = get_db_connection()

    rows = conn.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
    """).fetchall()

    conn.close()

    return jsonify([r["name"] for r in rows])

# ==========================================================
# Attendance Page
# ==========================================================
@attendance_bp.route("/attendance")
def attendance():
    """
    Render the main attendance page.

    Route:
        GET /attendance

    Returns:
        attendance.html template
    """
    return render_template("management/attendance.html")


# ==========================================================
# Load Attendance Records
# ==========================================================
@attendance_bp.route("/api/attendance")
def load_attendance():
    """
    Retrieve attendance records for a selected date.

    This endpoint is called asynchronously by attendance.js
    whenever the user selects a date on the attendance page.

    Route:
        GET /api/attendance?date=YYYY-MM-DD

    Returns:
        JSON list containing all children and their attendance
        status for the selected date.
    """
    date = request.args.get("date")

    conn = get_db_connection()

    rows = conn.execute("""
        SELECT
            c.child_id,
            c.first_name || ' ' || c.last_name AS child_name,

            a.status,
            a.check_in_time,
            a.check_out_time,
            a.pickup_by_parent_id,
            a.notes,

            r.room_id,
            r.room_name,

            p.first_name || ' ' || p.last_name AS pickup_by

        FROM child c

        LEFT JOIN child_attendance a
            ON c.child_id = a.child_id
        AND a.attendance_date = ?

        LEFT JOIN child_rooms cr
            ON c.child_id = cr.child_id
        AND cr.is_active = 1

        LEFT JOIN rooms r
            ON cr.room_id = r.room_id

        LEFT JOIN parent p
            ON a.pickup_by_parent_id = p.parent_id

        ORDER BY c.first_name
    """, (date,)).fetchall()

    children = [dict(row) for row in rows]

    # attach parents separately (for dropdown)
    for child in children:
        parents = conn.execute("""
            SELECT parent_id,
                first_name || ' ' || last_name AS name
            FROM parent
            WHERE household_id = (
                SELECT household_id
                FROM child
                WHERE child_id = ?
            )
        """, (child["child_id"],)).fetchall()

        child["parents"] = [dict(p) for p in parents]

    return jsonify(children)

# ==========================================================
# Load Educators list
# ==========================================================
@attendance_bp.route("/api/attendance/educators", methods=["GET"])
def get_educators():

    conn = get_db_connection()

    rows = conn.execute("""
        SELECT
            educator_id,
            educator_name AS name
        FROM educators
        ORDER BY educator_name
    """).fetchall()

    conn.close()

    return jsonify([
        {
            "id": r["educator_id"],
            "name": r["name"]
        }
        for r in rows
    ])


# ==========================================================
# Filtered rooms by educator
# ==========================================================
@attendance_bp.route("/api/attendance/room/<int:educator_id>", methods=["GET"])
def get_room_by_educator(educator_id):

    conn = get_db_connection()

    row = conn.execute("""
        SELECT
            r.room_id,
            r.room_name
        FROM educator_rooms er
        JOIN rooms r ON er.room_id = r.room_id
        WHERE er.educator_id = ?
        LIMIT 1
    """, (educator_id,)).fetchone()

    conn.close()

    if row:
        return jsonify({
            "id": row["room_id"],
            "name": row["room_name"]
        })

    return jsonify(None)

# ==========================================================
# Filter Session by Educator
# ==========================================================
@attendance_bp.route(
    "/api/attendance/session/<int:educator_id>",
    methods=["GET"]
)
def get_session_by_educator(educator_id):

    conn = get_db_connection()

    row = conn.execute("""
        SELECT
            session_id,
            session_type,
            room_id,
            start_time,
            end_time

        FROM attendance_sessions

        WHERE educator_id = ?

        ORDER BY created_at DESC
        LIMIT 1
    """, (educator_id,)).fetchone()

    conn.close()

    if row:

        return jsonify({
            "session_id": row["session_id"],
            "session_type": row["session_type"],
            "room_id": row["room_id"],
            "start_time": row["start_time"],
            "end_time": row["end_time"]
        })

    return jsonify(None)

# ==========================================================
# Sessions Management
# ==========================================================
@attendance_bp.route("/api/attendance/sessions", methods=["POST"])
def create_session():

    data = request.get_json()

    conn = get_db_connection()

    try:
        conn.execute("""
            INSERT INTO attendance_sessions (
                room_id,
                educator_id,
                session_type,
                start_time,
                end_time
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            data["room_id"],
            data["educator_id"],
            data["session_type"],
            data["start_time"],
            data["end_time"]
        ))

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Session created"
        })

    except Exception as e:

        conn.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        conn.close()

# ==========================================================
# Save attendance register with full audit history
# ==========================================================
@attendance_bp.route("/api/attendance/save-register", methods=["POST"])
def save_register():

    data = request.get_json()

    attendance_date = data["attendance_date"]
    room_id = data["room_id"]
    educator_id = data.get("educator_id")
    session_id = data.get("session_id")
    children = data["children"]

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        conn.execute("BEGIN")

        for child in children:

            child_id = child["child_id"]

            # --------------------------------------------------
            # CHECK IF RECORD EXISTS
            # --------------------------------------------------
            existing = cursor.execute("""
                SELECT *
                FROM child_attendance
                WHERE child_id = ?
                  AND room_id = ?
                  AND attendance_date = ?
                  AND (session_id = ? OR session_id IS NULL)
            """, (
                child_id,
                room_id,
                attendance_date,
                session_id
            )).fetchone()

            # --------------------------------------------------
            # CREATE SNAPSHOTS
            # --------------------------------------------------
            new_snapshot = {
                "child_id": child_id,
                "room_id": room_id,
                "educator_id": educator_id,
                "session_id": session_id,
                "attendance_date": attendance_date,
                "status": child.get("status"),
                "check_in_time": child.get("check_in_time"),
                "check_out_time": child.get("check_out_time"),
                "pickup_by_parent_id": child.get("pickup_by_parent_id"),
                "notes": child.get("notes")
            }

            # --------------------------------------------------
            # INSERT NEW RECORD
            # --------------------------------------------------
            if not existing:

                cursor.execute("""
                    INSERT INTO child_attendance (
                        child_id,
                        room_id,
                        educator_id,
                        session_id,
                        attendance_date,
                        status,
                        check_in_time,
                        check_out_time,
                        pickup_by_parent_id,
                        notes
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    child_id,
                    room_id,
                    educator_id,
                    session_id,
                    attendance_date,
                    child.get("status"),
                    child.get("check_in_time"),
                    child.get("check_out_time"),
                    child.get("pickup_by_parent_id"),
                    child.get("notes")
                ))

                attendance_id = cursor.lastrowid

                # history (create)
                cursor.execute("""
                    INSERT INTO child_attendance_history (
                        attendance_id,
                        action_type,
                        old_snapshot,
                        new_snapshot,
                        changed_by,
                        change_reason
                    )
                    VALUES (?, 'create', NULL, ?, ?, ?)
                """, (
                    attendance_id,
                    str(new_snapshot),
                    educator_id,
                    "Initial attendance entry"
                ))

            # --------------------------------------------------
            # UPDATE EXISTING RECORD
            # --------------------------------------------------
            else:

                attendance_id = existing["attendance_id"]

                old_snapshot = dict(existing)

                cursor.execute("""
                    UPDATE child_attendance
                    SET status = ?,
                        check_in_time = ?,
                        check_out_time = ?,
                        pickup_by_parent_id = ?,
                        notes = ?,
                        educator_id = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE attendance_id = ?
                """, (
                    child.get("status"),
                    child.get("check_in_time"),
                    child.get("check_out_time"),
                    child.get("pickup_by_parent_id"),
                    child.get("notes"),
                    educator_id,
                    attendance_id
                ))

                # history (update)
                cursor.execute("""
                    INSERT INTO child_attendance_history (
                        attendance_id,
                        action_type,
                        old_snapshot,
                        new_snapshot,
                        changed_by,
                        change_reason
                    )
                    VALUES (?, 'update', ?, ?, ?, ?)
                """, (
                    attendance_id,
                    str(old_snapshot),
                    str(new_snapshot),
                    educator_id,
                    "Register update"
                ))

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Attendance register saved"
        })

    except Exception as e:
        conn.rollback()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        conn.close()