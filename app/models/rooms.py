from app import db
from sqlalchemy import func


class Room(db.Model):
    __tablename__ = "rooms"
    __table_args__ = {"schema": "dbo"}

    room_id = db.Column(db.Integer, primary_key=True)

    branch_id = db.Column(
        db.Integer,
        db.ForeignKey("dbo.branches.branch_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    room_name = db.Column(db.Unicode(150), nullable=False)

    room_type = db.Column(db.Unicode(100), nullable=False, index=True)

    room_capacity = db.Column(db.Integer)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.sysutcdatetime(),
    )

    branch = db.relationship(
        "Branch",
        back_populates="rooms",
        lazy="selectin",
    )

    attendance_sessions = db.relationship(
        "AttendanceSession",
        back_populates="room",
        lazy="selectin",
    )

    child_attendance = db.relationship(
        "ChildAttendance",
        back_populates="room",
        lazy="selectin",
    )
