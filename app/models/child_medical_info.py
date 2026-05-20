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
