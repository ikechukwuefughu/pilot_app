from app import db
from sqlalchemy import func


class ChildAttendanceHistory(db.Model):
    __tablename__ = "child_attendance_history"
    __table_args__ = {"schema": "dbo"}

    history_id = db.Column(db.Integer, primary_key=True)

    attendance_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "dbo.child_attendance.attendance_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    action_type = db.Column(
        db.Unicode(10),
        nullable=False,
        index=True,
    )

    old_snapshot = db.Column(db.Text)

    new_snapshot = db.Column(db.Text)

    changed_by = db.Column(
        db.Integer,
        db.ForeignKey("dbo.educators.educator_id"),
        index=True,
    )

    change_reason = db.Column(db.Text)

    ip_address = db.Column(db.Unicode(50))

    device_info = db.Column(db.Text)

    changed_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.sysutcdatetime(),
    )

    attendance = db.relationship(
        "ChildAttendance",
        back_populates="history",
        lazy="selectin",
    )

    educator = db.relationship(
        "Educator",
        lazy="selectin",
    )
