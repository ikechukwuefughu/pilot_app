from app import db
from sqlalchemy import func

class EducatorAttendance(db.Model):
    __tablename__ = "educator_attendance"
    __table_args__ = {"schema": "dbo"}

    attendance_id = db.Column(db.Integer, primary_key=True)

    educator_id = db.Column(
        db.Integer,
        db.ForeignKey("dbo.educators.educator_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    attendance_date = db.Column(
        db.Date,
        nullable=False,
        index=True,
    )

    clock_in = db.Column(db.DateTime)

    clock_out = db.Column(db.DateTime)

    educator = db.relationship("Educator", lazy="selectin")
