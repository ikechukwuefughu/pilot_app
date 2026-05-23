# app/routes/management.py

from flask import Blueprint, render_template, request, jsonify
from app import db
from app.models import Household, Parent, Child, ChildContract, ChildMedicalInfo, ChildEmergencyContact, ChildParentRelationship, Branch, Room, Educator, EducatorRoom, EducatorWorkingHour, EducatorAttendance, AttendanceSession, ChildRoom, ChildAttendance, ChildAttendanceHistory
from datetime import datetime

def parse_date(val):
    if not val:
        return None
    try:
        return datetime.strptime(val, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None
management_bp = Blueprint(
    "management",
    __name__,
    url_prefix="/management"
)

# ==========================================================
# PAGE
# ==========================================================
@management_bp.route("/")
def management():
    return render_template("management/management.html")


# ==========================================================
# BRANCHES (SQLAlchemy)
# ==========================================================
@management_bp.route("/api/branches", methods=["GET", "POST"])
def branches():
    try:
        # ----------------------------------------------
        # GET BRANCHES
        # ----------------------------------------------
        if request.method == "GET":
            rows = (
                db.session.query(Branch)
                .order_by(Branch.branch_name)
                .all()
            )

            return jsonify([
                {
                    "id": b.branch_id,
                    "name": b.branch_name,
                }
                for b in rows
            ])

        # ----------------------------------------------
        # CREATE BRANCH
        # ----------------------------------------------
        data = request.get_json() or {}
        name = data.get("name")

        if not name:
            return jsonify({
                "success": False,
                "message": "Branch name is required",
            }), 400

        branch = Branch(branch_name=name)
        db.session.add(branch)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Branch created successfully",
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e),
        }), 500


# ==========================================================
# ROOMS (SQLAlchemy)
# ==========================================================
@management_bp.route("/api/rooms", methods=["GET", "POST"])
def rooms():
    try:
        if request.method == "GET":
            rows = (
                db.session.query(Room, Branch)
                .outerjoin(Branch, Room.branch_id == Branch.branch_id)
                .order_by(Branch.branch_name, Room.room_name)
                .all()
            )
            result = []
            for room, branch in rows:
                result.append({
                    "id": room.room_id,
                    "name": room.room_name,
                    "capacity": room.room_capacity,
                    "type": room.room_type,
                    "branch_id": room.branch_id,
                    "branch_name": branch.branch_name if branch else None,
                })
            return jsonify(result)

        data = request.get_json() or {}
        room = Room(
            branch_id=data.get("branch_id"),
            room_name=data.get("name"),
            room_capacity=data.get("capacity"),
            room_type=data.get("type"),
        )
        db.session.add(room)
        db.session.commit()
        return jsonify({"success": True, "message": "Room created successfully"})

    except Exception as e:
        db.session.rollback()
        import traceback
        return jsonify({
            "success": False,
            "message": str(e),
            "detail": traceback.format_exc()
        }), 500
# @management_bp.route("/api/rooms", methods=["GET", "POST"])
# def rooms():
#     try:
#         # ----------------------------------------------
#         # GET ROOMS
#         # ----------------------------------------------
#         if request.method == "GET":
#             rows = (
#                 db.session.query(Room, Branch)
#                 .outerjoin(Branch, Room.branch_id == Branch.branch_id)
#                 .order_by(Branch.branch_name, Room.room_name)
#                 .all()
#             )
#             result = []
#             for room, branch in rows:
#                 result.append({
#                     "id": room.room_id,
#                     "name": room.room_name,
#                     "capacity": room.room_capacity,
#                     "type": room.room_type,
#                     "branch_id": room.branch_id,
#                     "branch_name": branch.branch_name if branch else None,
#                 })
#             return jsonify(result)

#         # ----------------------------------------------
#         # CREATE ROOM
#         # ----------------------------------------------
#         data = request.get_json() or {}
#         room = Room(
#             branch_id=data.get("branch_id"),
#             room_name=data.get("name"),
#             room_capacity=data.get("capacity"),
#             room_type=data.get("type"),
#         )
#         db.session.add(room)
#         db.session.commit()
#         return jsonify({"success": True, "message": "Room created successfully"})

#     except Exception as e:
#         db.session.rollback()
#         import traceback
#         return jsonify({
#             "success": False,
#             "message": str(e),
#             "detail": traceback.format_exc()
#         }), 500

# ==========================================================
# EDUCATORS (SQLAlchemy)
# ==========================================================
@management_bp.route("/api/educators", methods=["GET", "POST", "PUT"])
def educators():
    try:
        # ----------------------------------------------
        # GET EDUCATORS
        # ----------------------------------------------
        if request.method == "GET":
            rows = (
                db.session.query(Educator)
                .order_by(Educator.educator_name)
                .all()
            )
            
            result = []
            
            for e in rows:
                room_ids = [er.room_id for er in e.educator_rooms]
                room_names = ", ".join(er.room.room_name for er in e.educator_rooms if er.room)
            
                result.append({
                    "id": e.educator_id,
                    "name": e.educator_name,
                    "phone": e.phone,
                    "email": e.email,
                    "role": e.role,
                    "status": e.status,
                    "start_date": e.start_date.isoformat() if e.start_date else None,  # fix
                    "end_date": e.end_date.isoformat() if e.end_date else None,        # fix
                    # "start_date": e.start_date,
                    # "end_date": e.end_date,
                    "room_ids": room_ids,
                    "rooms": room_names,
                })

            return jsonify(result)

        # ----------------------------------------------
        # CREATE EDUCATOR
        # ----------------------------------------------
        if request.method == "POST":
            data = request.get_json() or {}
            print("PUT data received:", data)  # check Render logs
            educator = Educator(
                educator_name=data.get("name"),
                phone=data.get("phone"),
                email=data.get("email"),
                role=data.get("role"),
                status="enabled",
                # start_date=data.get("start_date"),
                # end_date=data.get("end_date"),
                start_date=parse_date(data.get("start_date")),  # fix
                end_date=parse_date(data.get("end_date")),      # fix
            )

            db.session.add(educator)
            db.session.commit()

            return jsonify({
                "success": True,
                "message": "Educator created successfully",
            })

        # ----------------------------------------------
        # UPDATE EDUCATOR
        # ----------------------------------------------
        if request.method == "PUT":
            data = request.get_json() or {}
            educator_id = data.get("id")

            educator = db.session.get(Educator, educator_id)
            if not educator:
                return jsonify({
                    "success": False,
                    "message": "Educator not found",
                }), 404

            educator.educator_name = data.get("name")
            educator.phone = data.get("phone")
            educator.email = data.get("email")
            educator.role = data.get("role")
            # educator.start_date = data.get("start_date")
            # educator.end_date = data.get("end_date")
            educator.start_date = parse_date(data.get("start_date"))  # fix
            educator.end_date = parse_date(data.get("end_date"))      # fix

            db.session.commit()

            return jsonify({
                "success": True,
                "message": "Educator updated successfully",
            })

    except Exception as e:
        db.session.rollback()
    #     return jsonify({
    #         "success": False,
    #         "message": str(e),
    #     }), 500
        import traceback
        print(traceback.format_exc())  # prints full stack to server logs
        return jsonify({
        "success": False,
        "message": str(e),
        "detail": traceback.format_exc(),  # remove before production
    }), 500

# ==========================================================
# EDUCATOR ROOM ASSIGNMENT (SQLAlchemy)
# ==========================================================
@management_bp.route("/api/assign", methods=["POST"])
def assign_rooms():
    try:
        data = request.get_json() or {}

        educator_id = data.get("educator_id")
        new_room_ids = set(data.get("room_ids", []))

        if not educator_id:
            return jsonify({
                "success": False,
                "message": "Missing educator_id",
            }), 400

        # current active room assignments
        rows = (
            db.session.query(EducatorRoom)
            .filter(
                EducatorRoom.educator_id == educator_id,
                EducatorRoom.is_active == True,
            )
            .all()
        )

        current_room_ids = {r.room_id for r in rows}

        to_add = new_room_ids - current_room_ids
        to_remove = current_room_ids - new_room_ids

        # deactivate removed rooms
        if to_remove:
            (
                db.session.query(EducatorRoom)
                .filter(
                    EducatorRoom.educator_id == educator_id,
                    EducatorRoom.room_id.in_(to_remove),
                    EducatorRoom.is_active == True,
                )
                .update(
                    {
                        EducatorRoom.is_active: False,
                        # if you have unassigned_at column:
                        # EducatorRoom.unassigned_at: func.now(),
                    },
                    synchronize_session=False,
                )
            )

        # add new active rooms
        for room_id in to_add:
            er = EducatorRoom(
                educator_id=educator_id,
                room_id=room_id,
                is_active=True,
                # assigned_at can have default=func.now() in the model
            )
            db.session.add(er)

        db.session.commit()

        return jsonify({"success": True})

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e),
            "detail": traceback.format_exc()
        }), 500


# ==========================================================
# EDUCATOR ATTENDANCE (SQLAlchemy)
# ==========================================================
@management_bp.route("/api/attendance", methods=["POST"])
def educator_attendance():
    try:
        data = request.get_json() or {}

        attendance = EducatorAttendance(
            educator_id=data.get("educator_id"),
            attendance_date=data.get("date"),
            clock_in=data.get("clock_in"),
            clock_out=data.get("clock_out"),
        )

        db.session.add(attendance)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Attendance saved successfully",
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e),
        }), 500


# ==========================================================
# CHILDREN MANAGEMENT (SQLAlchemy)
# ==========================================================
@management_bp.route("/api/children", methods=["GET"])
def management_children():
    """
    Returns a list of children with:
      - assigned_room
      - contract_type / contract_status
      - household name
      - primary parent name + phone
    """
    # subquery to get latest active room per child
    latest_room_subq = (
        db.session.query(
            ChildRoom.child_id,
            ChildRoom.room_id,
        )
        .filter(ChildRoom.is_active == True)
        # add ordering if you have a start_date column
        # .order_by(ChildRoom.child_id, ChildRoom.start_date.desc())
        .subquery()
    )

    q = (
        db.session.query(
            Child.child_id,
            Child.first_name,
            Child.last_name,
            Child.date_of_birth,
            Room.room_name.label("assigned_room"),
            ChildContract.contract_type,
            ChildContract.status.label("contract_status"),
            Household.household_name.label("household"),
            (Parent.first_name + " " + Parent.last_name).label("parent"),
            Parent.phone.label("phone"),
        )
        .outerjoin(ChildContract, Child.child_id == ChildContract.child_id)
        .outerjoin(Household, Child.household_id == Household.household_id)
        .outerjoin(
            Parent,
            (Parent.household_id == Household.household_id)
            & (Parent.is_primary == True),
        )
        .outerjoin(
            latest_room_subq,
            latest_room_subq.c.child_id == Child.child_id,
        )
        .outerjoin(Room, latest_room_subq.c.room_id == Room.room_id)
    )

    rows = q.all()

    return jsonify([
        {
            "child_id": r.child_id,
            "first_name": r.first_name,
            "last_name": r.last_name,
            "assigned_room": r.assigned_room,
            "contract_type": r.contract_type,
            "contract_status": r.contract_status,
            "date_of_birth": r.date_of_birth,
            "household": r.household,
            "parent": r.parent,
            "phone": r.phone,
        }
        for r in rows
    ])


# ==========================================================
# CHILD ROOM ASSIGNMENT (SQLAlchemy)
# ==========================================================
@management_bp.route("/api/child-assign", methods=["POST"])
def assign_child_rooms():
    try:
        data = request.get_json() or {}

        child_id = data.get("child_id")
        new_room_ids = set(data.get("room_ids", []))

        if not child_id:
            return jsonify({
                "success": False,
                "message": "Missing child_id",
            }), 400

        # 1. close all current active rooms
        (
            db.session.query(ChildRoom)
            .filter(
                ChildRoom.child_id == child_id,
                ChildRoom.is_active == True,
            )
            .update(
                {
                    ChildRoom.is_active: False,
                    # if you have end_date: ChildRoom.end_date: func.now(),
                },
                synchronize_session=False,
            )
        )

        # 2. insert new room assignments
        for room_id in new_room_ids:
            cr = ChildRoom(
                child_id=child_id,
                room_id=room_id,
                is_active=True,
            )
            db.session.add(cr)

        db.session.commit()

        return jsonify({"success": True})

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e),
        }), 500


@management_bp.route("/api/child-assign/<int:child_id>", methods=["GET"])
def get_child_room(child_id):
    rows = (
        db.session.query(ChildRoom, Room)
        .join(Room, ChildRoom.room_id == Room.room_id)
        .filter(
            ChildRoom.child_id == child_id,
            ChildRoom.is_active == True,
        )
        # .order_by(ChildRoom.start_date.desc())  # if you have start_date
        .all()
    )

    return jsonify([
        {
            "room_id": cr.room_id,
            "room_name": room.room_name,
            "branch_id": room.branch_id,
        }
        for cr, room in rows
    ])
