# from flask import Blueprint, render_template, request, jsonify
# # from app.config import get_db_connection
# from app import db

# management_bp = Blueprint(
#     "management",
#     __name__,
#     url_prefix="/management"
# )

# ==========================================================
# PAGE
# ==========================================================

@management_bp.route("/")
def management():
    return render_template(
        "management/management.html"
    )

# # ==========================================================
# # BRANCHES
# # ==========================================================

# @management_bp.route("/api/branches", methods=["GET", "POST"])
# def branches():

#     conn = get_db_connection()

#     try:

#         # ======================================================
#         # GET BRANCHES
#         # ======================================================
#         if request.method == "GET":

#             rows = conn.execute("""
#                 SELECT
#                     branch_id,
#                     branch_name
#                 FROM branches
#                 ORDER BY branch_name
#             """).fetchall()

#             branches = [
#                 {
#                     "id": row["branch_id"],
#                     "name": row["branch_name"]
#                 }
#                 for row in rows
#             ]

#             return jsonify(branches)

#         # ======================================================
#         # CREATE BRANCH
#         # ======================================================
#         data = request.get_json()

#         conn.execute("""
#             INSERT INTO branches (
#                 branch_name
#             )
#             VALUES (?)
#         """, (
#             data["name"],
#         ))

#         conn.commit()

#         return jsonify({
#             "success": True,
#             "message": "Branch created successfully"
#         })

#     except Exception as e:

#         conn.rollback()

#         return jsonify({
#             "success": False,
#             "message": str(e)
#         }), 500

#     finally:
#         conn.close()

# # ==========================================================
# # ROOMS
# # ==========================================================

# @management_bp.route("/api/rooms", methods=["GET", "POST"])
# def rooms():

#     conn = get_db_connection()

#     try:

#         # ======================================================
#         # GET ROOMS
#         # ======================================================
#         if request.method == "GET":

#             rows = conn.execute("""
#                 SELECT
#                     r.room_id,
#                     r.room_name,
#                     r.room_capacity,
#                     r.room_type,
#                     r.branch_id,
#                     b.branch_name
#                 FROM rooms r

#                 LEFT JOIN branches b
#                     ON r.branch_id = b.branch_id

#                 ORDER BY
#                     b.branch_name,
#                     r.room_name
#             """).fetchall()

#             rooms = [
#                 {
#                     "id": row["room_id"],
#                     "name": row["room_name"],
#                     "capacity": row["room_capacity"],
#                     "type": row["room_type"],
#                     "branch_id": row["branch_id"],
#                     "branch_name": row["branch_name"]
#                 }
#                 for row in rows
#             ]

#             return jsonify(rooms)

#         # ======================================================
#         # CREATE ROOM
#         # ======================================================
#         data = request.get_json()

#         conn.execute("""
#             INSERT INTO rooms (
#                 branch_id,
#                 room_name,
#                 room_capacity,
#                 room_type
#             )
#             VALUES (?, ?, ?, ?)
#         """, (
#             data["branch_id"],
#             data["name"],
#             data["capacity"],
#             data.get("type", "General")
#         ))

#         conn.commit()

#         return jsonify({
#             "success": True,
#             "message": "Room created successfully"
#         })

#     except Exception as e:

#         conn.rollback()

#         return jsonify({
#             "success": False,
#             "message": str(e)
#         }), 500

#     finally:
#         conn.close()

# # ==========================================================
# # EDUCATORS
# # ==========================================================

# @management_bp.route("/api/educators", methods=["GET", "POST", "PUT"])
# def educators():

#     conn = get_db_connection()

#     try:

#         # ======================================================
#         # GET EDUCATORS
#         # ======================================================
#         if request.method == "GET":

#             rows = conn.execute("""
#                 SELECT
#                     educator_id,
#                     educator_name,
#                     phone,
#                     email,
#                     role,
#                     status,
#                     start_date,
#                     end_date
#                 FROM educators
#                 ORDER BY educator_name
#             """).fetchall()

#             educators = []

#             for row in rows:

#                 room_rows = conn.execute("""
#                     SELECT
#                         er.room_id, r.room_name
#                     FROM educator_rooms er

#                     LEFT JOIN rooms r
#                         ON er.room_id = r.room_id

#                     WHERE er.educator_id = ?
#                 """, (
#                     row["educator_id"],
#                 )).fetchall()

#                 room_ids = [r["room_id"] 
#                     for r in room_rows]
#                 room_names = ", ".join([
#                     room["room_name"]
#                     for room in room_rows
#                 ])

#                 educators.append({
#                     "id": row["educator_id"],
#                     "name": row["educator_name"],
#                     "phone": row["phone"],
#                     "email": row["email"],
#                     "role": row["role"],
#                     "status": row["status"],
#                     "start_date": row["start_date"],
#                     "end_date": row["end_date"],
#                     "room_ids": room_ids,
#                     "rooms": room_names
#                 })

#             return jsonify(educators)

#         # ======================================================
#         # CREATE EDUCATOR
#         # ======================================================
#         if request.method == "POST":

#             data = request.get_json()

#             conn.execute("""
#                 INSERT INTO educators (
#                     educator_name,
#                     phone,
#                     email,
#                     role,
#                     status,
#                     start_date,
#                     end_date
#                 )
#                 VALUES (?, ?, ?, ?, ?, ?, ?)
#             """, (
#                 data["name"],
#                 data["phone"],
#                 data["email"],
#                 data["role"],
#                 "Enabled",
#                 data["start_date"],
#                 data["end_date"]
#             ))

#             conn.commit()

#             return jsonify({
#                 "success": True,
#                 "message": "Educator created successfully"
#             })

#         # ======================================================
#         # UPDATE EDUCATOR
#         # ======================================================
#         if request.method == "PUT":

#             data = request.get_json()

#             conn.execute("""
#                 UPDATE educators

#                 SET
#                     educator_name = ?,
#                     phone = ?,
#                     email = ?,
#                     role = ?,
#                     start_date = ?,
#                     end_date = ?

#                 WHERE educator_id = ?
#             """, (
#                 data["name"],
#                 data["phone"],
#                 data["email"],
#                 data["role"],
#                 data["start_date"],
#                 data["end_date"],
#                 data["id"]
#             ))

#             conn.commit()

#             return jsonify({
#                 "success": True,
#                 "message": "Educator updated successfully"
#             })

#     except Exception as e:

#         conn.rollback()

#         return jsonify({
#             "success": False,
#             "message": str(e)
#         }), 500

#     finally:
#         conn.close()

# # ==========================================================
# # EDUCATOR ROOM ASSIGNMENT
# # ==========================================================

# @management_bp.route("/api/assign", methods=["POST"])
# def assign_rooms():

#     conn = get_db_connection()

#     try:

#         data = request.get_json()

#         educator_id = data.get("educator_id")
#         new_room_ids = set(data.get("room_ids", []))

#         print("EDUCATOR ASSIGNMENT:", data)

#         if not educator_id:

#             return jsonify({
#                 "success": False,
#                 "message": "Missing educator_id"
#             }), 400

#         # ==================================================
#         # CURRENT ACTIVE ROOM ASSIGNMENTS
#         # ==================================================

#         rows = conn.execute("""

#             SELECT
#                 educator_room_id,
#                 room_id

#             FROM educator_rooms

#             WHERE educator_id = ?
#             AND is_active = 1

#         """, (educator_id,)).fetchall()

#         current_room_ids = {
#             r["room_id"]
#             for r in rows
#         }

#         # ==================================================
#         # FIND CHANGES
#         # ==================================================

#         to_add = new_room_ids - current_room_ids

#         to_remove = current_room_ids - new_room_ids

#         # ==================================================
#         # DEACTIVATE REMOVED ROOMS
#         # ==================================================

#         for room_id in to_remove:

#             conn.execute("""

#                 UPDATE educator_rooms

#                 SET
#                     is_active = 0,
#                     unassigned_at = CURRENT_TIMESTAMP

#                 WHERE educator_id = ?
#                 AND room_id = ?
#                 AND is_active = 1

#             """, (educator_id, room_id))

#         # ==================================================
#         # ADD NEW ACTIVE ROOMS
#         # ==================================================

#         for room_id in to_add:

#             conn.execute("""

#                 INSERT INTO educator_rooms (

#                     educator_id,
#                     room_id,
#                     assigned_at,
#                     is_active

#                 )
#                 VALUES (

#                     ?,
#                     ?,
#                     CURRENT_TIMESTAMP,
#                     1

#                 )

#             """, (

#                 educator_id,
#                 room_id

#             ))

#         conn.commit()

#         return jsonify({
#             "success": True
#         })

#     except Exception as e:

#         conn.rollback()

#         print("ASSIGNMENT ERROR:", str(e))

#         return jsonify({
#             "success": False,
#             "message": str(e)
#         }), 500

#     finally:

#         conn.close()

# # ==========================================================
# # ATTENDANCE
# # ==========================================================

# @management_bp.route("/api/attendance", methods=["POST"])
# def attendance():

#     conn = get_db_connection()

#     try:

#         data = request.get_json()

#         conn.execute("""
#             INSERT INTO educator_attendance (
#                 educator_id,
#                 attendance_date,
#                 clock_in,
#                 clock_out
#             )
#             VALUES (?, ?, ?, ?)
#         """, (
#             data["educator_id"],
#             data["date"],
#             data["clock_in"],
#             data["clock_out"]
#         ))

#         conn.commit()

#         return jsonify({
#             "success": True,
#             "message": "Attendance saved successfully"
#         })

#     except Exception as e:

#         conn.rollback()

#         return jsonify({
#             "success": False,
#             "message": str(e)
#         }), 500

#     finally:
#         conn.close()

# # ==========================================================
# # CHILDREN MANAGEMENT
# # ==========================================================

# @management_bp.route("/api/children", methods=["GET"])
# def children():

#     conn = get_db_connection()

#     rows = conn.execute("""
#     SELECT
#         c.child_id,
#         c.first_name,
#         c.last_name,
#         c.date_of_birth,

#         (
#             SELECT r.room_name
#             FROM child_rooms cr
#             JOIN rooms r ON cr.room_id = r.room_id
#             WHERE cr.child_id = c.child_id
#             AND cr.is_active = 1
#             ORDER BY cr.start_date DESC
#             LIMIT 1
#         ) AS assigned_room,

#         ct.contract_type,
#         ct.status AS contract_status,

#         h.household_name AS household,

#         p.first_name || ' ' || p.last_name AS parent,
#         p.phone AS phone

#     FROM child c

#     LEFT JOIN child_contracts ct
#         ON c.child_id = ct.child_id

#     LEFT JOIN household h
#         ON c.household_id = h.household_id

#     LEFT JOIN parent p
#         ON p.household_id = h.household_id
#         AND p.is_primary = 1
# """).fetchall()

#     conn.close()

#     return jsonify([
#         {
#             "child_id": r["child_id"],
#             "first_name": r["first_name"],
#             "last_name": r["last_name"],
#             "assigned_room": r["assigned_room"],
#             "contract_type": r["contract_type"],
#             "contract_status": r["contract_status"],
#             "date_of_birth": r["date_of_birth"],
#             "household": r["household"],
#             "parent": r["parent"],
#             "phone": r["phone"]
#         }
#         for r in rows
#     ])

# @management_bp.route("/api/child-assign", methods=["POST"])
# def assign_child_rooms():

#     conn = get_db_connection()

#     try:
#         data = request.get_json()

#         print("CHILD ASSIGN DATA:", data)

#         child_id = data.get("child_id")
#         new_room_ids = set(data.get("room_ids", []))

#         if not child_id:
#             return jsonify({
#                 "success": False,
#                 "message": "Missing child_id"
#             }), 400

#         # ======================================================
#         # 1. CLOSE ALL CURRENT ACTIVE ROOMS (HISTORY SAFE)
#         # ======================================================
#         conn.execute("""
#             UPDATE child_rooms
#             SET is_active = 0,
#                 end_date = CURRENT_TIMESTAMP
#             WHERE child_id = ?
#             AND is_active = 1
#         """, (child_id,))

#         # ======================================================
#         # 2. INSERT NEW ROOM ASSIGNMENTS
#         # ======================================================
#         for room_id in new_room_ids:

#             conn.execute("""
#                 INSERT INTO child_rooms (
#                     child_id,
#                     room_id,
#                     is_active
#                 )
#                 VALUES (?, ?, 1)
#             """, (child_id, room_id))

#         conn.commit()

#         return jsonify({
#             "success": True
#         })

#     except Exception as e:

#         conn.rollback()

#         print("CHILD ASSIGN ERROR:", str(e))

#         return jsonify({
#             "success": False,
#             "message": str(e)
#         }), 500

#     finally:
#         conn.close()

# @management_bp.route("/api/child-assign/<int:child_id>", methods=["GET"])
# def get_child_room(child_id):

#     conn = get_db_connection()

#     rows = conn.execute("""
#         SELECT
#             cr.room_id,
#             r.room_name,
#             r.branch_id
#         FROM child_rooms cr
#         JOIN rooms r ON cr.room_id = r.room_id
#         WHERE cr.child_id = ?
#         AND cr.is_active = 1
#         ORDER BY cr.start_date DESC
#     """, (child_id,)).fetchall()

#     conn.close()

#     return jsonify([
#         {
#             "room_id": r["room_id"],
#             "room_name": r["room_name"],
#             "branch_id": r["branch_id"]
#         }
#         for r in rows
#     ])
