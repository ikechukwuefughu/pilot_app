from app import db
from sqlalchemy import func

class ChildParentRelationship(db.Model):
    __tablename__ = "child_parent_relationship"
    __table_args__ = {"schema": "dbo"}

    relationship_id = db.Column(db.Integer, primary_key=True)

    child_id = db.Column(
        db.Integer,
        db.ForeignKey("dbo.child.child_id", ondelete="CASCADE"),
        index=True
    )

    parent_id = db.Column(
        db.Integer,
        db.ForeignKey("dbo.parent.parent_id", ondelete="CASCADE"),
        index=True
    )

    relationship_type = db.Column(db.Unicode(100), nullable=False)

    legal_guardian = db.Column(db.Boolean, server_default=db.text("0"))
    authorized_pickup = db.Column(db.Boolean, server_default=db.text("1"))
    emergency_contact = db.Column(db.Boolean, server_default=db.text("1"))

    def to_dict(self):
    return {
        "relationship_id": self.relationship_id,
        "child_id": self.child_id,
        "parent_id": self.parent_id,
        "relationship_type": self.relationship_type,
        "legal_guardian": self.legal_guardian,
        "authorized_pickup": self.authorized_pickup,
        "emergency_contact": self.emergency_contact
    }
