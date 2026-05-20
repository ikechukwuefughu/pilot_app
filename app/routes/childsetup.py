from flask import Blueprint, render_template, request, jsonify, current_app
from app import db
from app.models import Household, Parent, Child, ChildContract, ChildMedicalInfo, ChildEmergencyContact, ChildParentRelationship
from datetime import date

children_bp = Blueprint("children",__name__,url_prefix="/children")

# ==========================================================
# PAGE VIEW
# ==========================================================
@children_bp.route("/")
def child_setup():
    return render_template("registration/children/child.html")

# ==========================================================
# SAVE CHILDREN (FULL UPSERT)
# ==========================================================
@children_bp.route("/api/child/setup", methods=["POST"])
def save_children():

    data = request.get_json()
    household_id = data.get("household_id")
    children = data.get("children", [])

    if not household_id:
        return jsonify({"success": False, "error": "household_id required"}), 400

    try:
        for c in children:

            child_id = c.get("child_id")
            contract = c.get("contract", {})
            medical = c.get("medical", {})
            emergency_contacts = c.get("emergency_contacts", []) or []
            relationships = c.get("relationships", []) or []

            # ==================================================
            # STATUS
            # ==================================================
            status = "Active"
            if contract.get("end_date"):
                try:
                    if date.fromisoformat(contract["end_date"]) < date.today():
                        status = "Inactive"
                except:
                    pass

            # ==================================================
            # CHILD UPSERT
            # ==================================================
            if child_id:
                child_obj = Child.query.get(child_id)
            else:
                child_obj = Child()
                db.session.add(child_obj)

            child_obj.household_id = household_id
            child_obj.first_name = c.get("first_name")
            child_obj.last_name = c.get("last_name")
            child_obj.date_of_birth = c.get("date_of_birth")
            child_obj.ppsn = c.get("ppsn")
            child_obj.chick_code = c.get("chick_code")
            child_obj.ecce_eligible = bool(c.get("ecce_eligible"))
            child_obj.start_date = c.get("start_date")

            db.session.flush()  # ensures child_id exists
            child_id = child_obj.child_id

            # ==================================================
            # CONTRACT UPSERT
            # ==================================================
            contract_id = contract.get("contract_id")

            if contract_id:
                contract_obj = ChildContract.query.get(contract_id)
            else:
                contract_obj = ChildContract(child_id=child_id)
                db.session.add(contract_obj)

            contract_obj.contract_type = contract.get("type")
            contract_obj.start_date = contract.get("start_date")
            contract_obj.end_date = contract.get("end_date")
            contract_obj.agreed_hours_per_week = contract.get("hours_per_week")
            contract_obj.hourly_rate = contract.get("hourly_rate")
            contract_obj.subsidy_rate = contract.get("subsidy_rate")
            contract_obj.status = status

            # ==================================================
            # MEDICAL INFO (UPSERT 1:1)
            # ==================================================

            medical_obj = ChildMedicalInfo.query.filter_by(child_id=child_id).first()

            if not medical_obj:
                medical_obj = ChildMedicalInfo(child_id=child_id)
                db.session.add(medical_obj)

            medical_obj.allergies = medical.get("allergies")
            medical_obj.medical_notes = medical.get("medical_notes")

            # ==================================================
            # EMERGENCY CONTACTS (REPLACE + LIMIT 4)
            # ==================================================
            if len(emergency_contacts) > 4:
                return jsonify({
                    "success": False,
                    "error": "Maximum 4 emergency contacts allowed per child"
                }), 400

            ChildEmergencyContact.query.filter_by(child_id=child_id).delete()

            for ec in emergency_contacts:
                db.session.add(ChildEmergencyContact(
                    child_id=child_id,
                    first_name=ec.get("first_name"),
                    last_name=ec.get("last_name"),
                    relationship_to_child=ec.get("relationship"),
                    phone=ec.get("phone"),
                    authorized_pickup=bool(ec.get("authorized_pickup"))
                ))

            # ==================================================
            # PARENT RELATIONSHIPS (REPLACE)
            # ==================================================
            ChildParentRelationship.query.filter_by(child_id=child_id).delete()

            for rel in relationships:
                db.session.add(ChildParentRelationship(
                    child_id=child_id,
                    parent_id=rel.get("parent_id"),
                    relationship_type=rel.get("relationship"),
                    legal_guardian=bool(rel.get("is_legal_guardian")),
                    authorized_pickup=False,
                    emergency_contact=False
                ))

        db.session.commit()

        return jsonify({"success": True, "message": "Saved successfully"})

    except Exception as e:
        db.session.rollback()
        import traceback
        return jsonify({
            "success": False,
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500

    finally:
        conn.close()

@children_bp.route("/api/household/<int:household_id>", methods=["GET"])
def get_household(household_id):

    household = db.session.get(Household, household_id)
    parents = Parent.query.filter_by(household_id=household_id).all()
    children = Child.query.filter_by(household_id=household_id).all()

    result_children = []

    for c in children:
    
        contracts = ChildContract.query.filter_by(child_id=c.child_id).all()
        medical = ChildMedicalInfo.query.filter_by(child_id=c.child_id).first()
        emergency = ChildEmergencyContact.query.filter_by(child_id=c.child_id).all()
        relationships = ChildParentRelationship.query.filter_by(child_id=c.child_id).all()
    
        base = c.to_dict() if hasattr(c, "to_dict") else {
            "child_id": c.child_id,
            "first_name": c.first_name,
            "last_name": c.last_name,
            "date_of_birth": c.date_of_birth,
            "ppsn": c.ppsn,
            "chick_code": c.chick_code,
            "ecce_eligible": c.ecce_eligible,
            "start_date": c.start_date
        }
    
        result_children.append({
            **base,
            "contracts": [x.to_dict() for x in contracts] if contracts else [],
            "medical": medical.to_dict() if medical else {},
            "emergency_contacts": [x.to_dict() for x in emergency],
            "relationships": [x.to_dict() for x in relationships]
        })
    
        return jsonify({
            "household": household.to_dict() if household else None,
            "parents": [p.to_dict() for p in parents],
            "children": result_children
        })
