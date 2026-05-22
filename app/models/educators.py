from app import db
from sqlalchemy import func


class Educator(db.Model):
    __tablename__ = "educators"
    __table_args__ = {"schema": "dbo"}

    educator_id = db.Column(db.Integer, primary_key=True)

    educator_name = db.Column(db.Unicode(150), nullable=False, index=True)

    phone = db.Column(db.Unicode(30))

    email = db.Column(db.Unicode(254), index=True)

    role = db.Column(
        db.Unicode(20),
        nullable=False,
        server_default=db.text("'educator'"),
        index=True,
    )

    status = db.Column(
        db.Unicode(20),
        nullable=False,
        server_default=db.text("'enabled'"),
        index=True,
    )

    verified = db.Column(
        db.Boolean,
        nullable=False,
        server_default=db.text("0"),
        index=True,
    )

    start_date = db.Column(db.Date)

    end_date = db.Column(db.Date)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.sysutcdatetime(),
    )

    attendance_sessions = db.relationship(
        "AttendanceSession",
        back_populates="educator",
        lazy="selectin",
    )

    child_attendance = db.relationship(
        "ChildAttendance",
        back_populates="educator",
        lazy="selectin",
    )
