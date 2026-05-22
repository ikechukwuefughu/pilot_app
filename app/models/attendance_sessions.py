from app import db
from sqlalchemy import func


class AttendanceSession(db.Model):
    __tablename__ = "attendance_sessions"
    __table_args__ = (
        db.UniqueConstraint(
            "room_id",
            "session_type",
            name="UQ_attendance_sessions_room_type",
        ),
        {"schema": "dbo"},
    )

    session_id = db.Column(db.Integer, primary_key=True)

    room_id = db.Column(
        db.Integer,
        db.ForeignKey("dbo.rooms.room_id"),
        nullable=False,
        index=True,
    )

    educator_id = db.Column(
        db.Integer,
        db.ForeignKey("dbo.educators.educator_id"),
        nullable=False,
        index=True,
    )

    session_type = db.Column(
        db.Unicode(20),
        nullable=False,
        index=True,
    )

    start_time = db.Column(db.Time)

    end_time = db.Column(db.Time)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.sysutcdatetime(),
    )

    room = db.relationship(
        "Room",
        back_populates="attendance_sessions",
        lazy="selectin",
    )

    educator = db.relationship(
        "Educator",
        back_populates="attendance_sessions",
        lazy="selectin",
    )

    attendance_records = db.relationship(
        "ChildAttendance",
        back_populates="session",
        lazy="selectin",
    )
