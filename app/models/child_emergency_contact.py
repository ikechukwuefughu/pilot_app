from app import db
from sqlalchemy import func

class ChildEmergencyContact(db.Model):
    __tablename__ = "child_emergency_contact"
    __table_args__ = {"schema": "dbo"}

    emergency_contact_id = db.Column(db.Integer, primary_key=True)

    child_id = db.Column(
        db.Integer,
        db.ForeignKey("dbo.child.child_id", ondelete="CASCADE"),
        index=True
    )

    first_name = db.Column(db.Unicode(100))
    last_name = db.Column(db.Unicode(100))
    relationship_to_child = db.Column(db.Unicode(100))
    phone = db.Column(db.Unicode(50))

    authorized_pickup = db.Column(db.Boolean, server_default=db.text("0"))
