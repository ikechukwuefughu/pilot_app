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

# app/routes/attendance.py

from flask import Blueprint, render_template, request, jsonify
from app import db
from app.models import Household, Parent, Child, ChildContract, ChildMedicalInfo, ChildEmergencyContact, ChildParentRelationship, Branch, Room, Educator, EducatorRoom, EducatorWorkingHour, EducatorAttendance, AttendanceSession, ChildRoom, ChildAttendance, ChildAttendanceHistory

attendance_bp = Blueprint("attendance", __name__)

# ==========================================================
# Attendance Page
# ==========================================================
@attendance_bp.route("/attendance")
def attendance():
    return render_template("management/attendance.html")


# ==========================================================
# Load Attendance Records (SQLAlchemy)
# ==========================================================
@attendance_bp.route("/api/attendance", methods=["GET"])
def load_attendance():
    """
    GET /api/attendance?date=YYYY-MM-DD

    Returns:
        JSON list of children with attendance + parents list
        for the selected date.
    """
    selected_date = request.args.get("date")
    if not selected_date:
        return jsonify({"success": False, "error": "date is required"}), 400

    # Base query, equivalent to your LEFT JOINs
    q = (
        db.session.query(
            Child.child_id,
            (Child.first_name + " " + Child.last_name).label("child_name"),
            ChildAttendance.status,
            ChildAttendance.check_in_time,
            ChildAttendance.check_out_time,
            ChildAttendance.pickup_by_parent_id,
            ChildAttendance.notes,
            Room.room_id,
            Room.room_name,
            (Parent.first_name + " " + Parent.last_name).label("pickup_by"),
        )
        .outerjoin(
            ChildAttendance,
            (ChildAttendance.child_id == Child.child_id)
            & (ChildAttendance.attendance_date == selected_date),
        )
        .outerjoin(
            ChildRoom,
            (ChildRoom.child_id == Child.child_id)
            & (ChildRoom.is_active == True),
        )
        .outerjoin(Room, ChildRoom.room_id == Room.room_id)
        .outerjoin(
            Parent,
            ChildAttendance.pickup_by_parent_id == Parent.parent_id,
        )
        .order_by(Child.first_name)
    )

    rows = q.all()

    children = []
    for row in rows:
        child_dict = {
            "child_id": row.child_id,
            "child_name": row.child_name,
            "status": row.status,
            "check_in_time": row.check_in_time,
            "check_out_time": row.check_out_time,
            "pickup_by_parent_id": row.pickup_by_parent_id,
            "notes": row.notes,
            "room_id": row.room_id,
            "room_name": row.room_name,
            "pickup_by": row.pickup_by,
        }

        # Fetch parents for this child (household-based)
        parents = (
            db.session.query(Parent)
            .join(Child, Child.household_id == Parent.household_id)
            .filter(Child.child_id == row.child_id)
            .all()
        )

        child_dict["parents"] = [
            {
                "parent_id": p.parent_id,
                "name": f"{p.first_name} {p.last_name}",
            }
            for p in parents
        ]

        children.append(child_dict)

    return jsonify(children)


# ==========================================================
# Load Educators list (SQLAlchemy)
# ==========================================================
@attendance_bp.route("/api/attendance/educators", methods=["GET"])
def get_educators():
    educators = (
        db.session.query(Educator)
        .order_by(Educator.educator_name)
        .all()
    )

    return jsonify(
        [
            {
                "id": e.educator_id,
                "name": e.educator_name,
            }
            for e in educators
        ]
    )


# ==========================================================
# Filter rooms by educator (SQLAlchemy)
# ==========================================================
@attendance_bp.route(
    "/api/attendance/room/<int:educator_id>",
    methods=["GET"],
)
def get_room_by_educator(educator_id):
    room = (
        db.session.query(Room)
        .join(EducatorRoom, EducatorRoom.room_id == Room.room_id)
        .filter(EducatorRoom.educator_id == educator_id)
        .first()
    )

    if room:
        return jsonify(
            {
                "id": room.room_id,
                "name": room.room_name,
            }
        )

    return jsonify(None)


# ==========================================================
# Filter Session by Educator (SQLAlchemy)
# ==========================================================
@attendance_bp.route(
    "/api/attendance/session/<int:educator_id>",
    methods=["GET"],
)
def get_session_by_educator(educator_id):
    session = (
        db.session.query(AttendanceSession)
        .filter(AttendanceSession.educator_id == educator_id)
        .order_by(AttendanceSession.created_at.desc())
        .first()
    )

    if session:
        return jsonify(
            {
                "session_id": session.session_id,
                "session_type": session.session_type,
                "room_id": session.room_id,
                "start_time": session.start_time,
                "end_time": session.end_time,
            }
        )

    return jsonify(None)


# ==========================================================
# Sessions Management (SQLAlchemy)
# ==========================================================
@attendance_bp.route("/api/attendance/sessions", methods=["POST"])
def create_session():
    data = request.get_json() or {}

    try:
        session = AttendanceSession(
            room_id=data["room_id"],
            educator_id=data["educator_id"],
            session_type=data["session_type"],
            start_time=data["start_time"],
            end_time=data["end_time"],
        )

        db.session.add(session)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "Session created",
                "session_id": session.session_id,
            }
        )

    except Exception as e:
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "message": str(e),
                }
            ),
            500,
        )


# ==========================================================
# Save attendance register with full audit history (SQLAlchemy)
# ==========================================================
@attendance_bp.route(
    "/api/attendance/save-register",
    methods=["POST"],
)
def save_register():
    """
    POST body:

    {
      "attendance_date": "YYYY-MM-DD",
      "room_id": 1,
      "educator_id": 2,
      "session_id": 3 or null,
      "children": [
        {
          "child_id": 10,
          "status": "Present",
          "check_in_time": "09:00",
          "check_out_time": "15:00",
          "pickup_by_parent_id": 5,
          "notes": "Some note"
        },
        ...
      ]
    }
    """
    data = request.get_json() or {}

    attendance_date = data.get("attendance_date")
    room_id = data.get("room_id")
    educator_id = data.get("educator_id")
    session_id = data.get("session_id")
    children = data.get("children", [])

    if not attendance_date or not room_id or children is None:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "attendance_date, room_id and children are required",
                }
            ),
            400,
        )

    try:
        for child_data in children:
            child_id = child_data["child_id"]

            # Check if record exists for this child/date/room/session
            existing = (
                db.session.query(ChildAttendance)
                .filter(
                    ChildAttendance.child_id == child_id,
                    ChildAttendance.room_id == room_id,
                    ChildAttendance.attendance_date == attendance_date,
                    # session match or null (same as old SQL)
                    db.or_(
                        ChildAttendance.session_id == session_id,
                        ChildAttendance.session_id.is_(None),
                    ),
                )
                .first()
            )

            new_snapshot = {
                "child_id": child_id,
                "room_id": room_id,
                "educator_id": educator_id,
                "session_id": session_id,
                "attendance_date": attendance_date,
                "status": child_data.get("status"),
                "check_in_time": child_data.get("check_in_time"),
                "check_out_time": child_data.get("check_out_time"),
                "pickup_by_parent_id": child_data.get("pickup_by_parent_id"),
                "notes": child_data.get("notes"),
            }

            if not existing:
                # Insert new attendance
                attendance = ChildAttendance(
                    child_id=child_id,
                    room_id=room_id,
                    educator_id=educator_id,
                    session_id=session_id,
                    attendance_date=attendance_date,
                    status=child_data.get("status"),
                    check_in_time=child_data.get("check_in_time"),
                    check_out_time=child_data.get("check_out_time"),
                    pickup_by_parent_id=child_data.get("pickup_by_parent_id"),
                    notes=child_data.get("notes"),
                )
                db.session.add(attendance)
                db.session.flush()  # get attendance_id

                history = ChildAttendanceHistory(
                    attendance_id=attendance.attendance_id,
                    action_type="create",
                    old_snapshot=None,
                    new_snapshot=str(new_snapshot),
                    changed_by=educator_id,
                    change_reason="Initial attendance entry",
                )
                db.session.add(history)

            else:
                # Update existing
                old_snapshot = {
                    "attendance_id": existing.attendance_id,
                    "child_id": existing.child_id,
                    "room_id": existing.room_id,
                    "educator_id": existing.educator_id,
                    "session_id": existing.session_id,
                    "attendance_date": existing.attendance_date,
                    "status": existing.status,
                    "check_in_time": existing.check_in_time,
                    "check_out_time": existing.check_out_time,
                    "pickup_by_parent_id": existing.pickup_by_parent_id,
                    "notes": existing.notes,
                }

                existing.status = child_data.get("status")
                existing.check_in_time = child_data.get("check_in_time")
                existing.check_out_time = child_data.get("check_out_time")
                existing.pickup_by_parent_id = child_data.get("pickup_by_parent_id")
                existing.notes = child_data.get("notes")
                existing.educator_id = educator_id

                history = ChildAttendanceHistory(
                    attendance_id=existing.attendance_id,
                    action_type="update",
                    old_snapshot=str(old_snapshot),
                    new_snapshot=str(new_snapshot),
                    changed_by=educator_id,
                    change_reason="Register update",
                )
                db.session.add(history)

        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "Attendance register saved",
            }
        )

    except Exception as e:
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "message": str(e),
                }
            ),
            500,
        )
