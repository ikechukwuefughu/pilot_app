from app import db
from sqlalchemy import func


class ChildAttendance(db.Model):
    __tablename__ = "child_attendance"
    __table_args__ = (
        db.UniqueConstraint(
            "child_id",
            "room_id",
            "attendance_date",
            "session_id",
            name="UQ_child_attendance",
        ),
        {"schema": "dbo"},
    )

    attendance_id = db.Column(db.Integer, primary_key=True)

    child_id = db.Column(
        db.Integer,
        db.ForeignKey("dbo.child.child_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    room_id = db.Column(
        db.Integer,
        db.ForeignKey("dbo.rooms.room_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    educator_id = db.Column(
        db.Integer,
        db.ForeignKey("dbo.educators.educator_id"),
        index=True,
    )

    session_id = db.Column(
        db.Integer,
        db.ForeignKey("dbo.attendance_sessions.session_id"),
        index=True,
    )

    attendance_date = db.Column(
        db.Date,
        nullable=False,
        index=True,
    )

    status = db.Column(
        db.Unicode(10),
        index=True,
    )

    check_in_time = db.Column(db.Time)

    check_out_time = db.Column(db.Time)

    pickup_by_parent_id = db.Column(
        db.Integer,
        db.ForeignKey("dbo.parent.parent_id"),
    )

    notes = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.sysutcdatetime(),
    )

    updated_at = db.Column(db.DateTime)

    child = db.relationship(
        "Child",
        back_populates="attendance",
        lazy="selectin",
    )

    room = db.relationship(
        "Room",
        back_populates="child_attendance",
        lazy="selectin",
    )

    educator = db.relationship(
        "Educator",
        back_populates="child_attendance",
        lazy="selectin",
    )

    session = db.relationship(
        "AttendanceSession",
        back_populates="attendance_records",
        lazy="selectin",
    )

    pickup_parent = db.relationship(
        "Parent",
        lazy="selectin",
    )
    )
