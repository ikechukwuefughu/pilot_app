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

    educator_rooms = db.relationship(
        "EducatorRoom",
        back_populates="room",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    
    def to_dict(self):
        return {
            "room_id": self.room_id,
            "branch_id": self.branch_id,
            "room_name": self.room_name,
            "room_type": self.room_type,
            "room_capacity": self.room_capacity,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
