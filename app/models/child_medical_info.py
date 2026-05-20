from app import db
from sqlalchemy import func

class ChildMedicalInfo(db.Model):
    __tablename__ = "child_medical_info"
    __table_args__ = {"schema": "dbo"}

    medical_id = db.Column(db.Integer, primary_key=True)

    child_id = db.Column(
        db.Integer,
        db.ForeignKey("dbo.child.child_id", ondelete="CASCADE"),
        unique=True,
        index=True
    )

    allergies = db.Column(db.UnicodeText)
    medical_notes = db.Column(db.UnicodeText)

    def to_dict(self):
        return {
            "medical_id": self.medical_id,
            "child_id": self.child_id,
            "allergies": self.allergies,
            "medical_notes": self.medical_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
