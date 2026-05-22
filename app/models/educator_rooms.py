from app import db
from sqlalchemy import func


class EducatorRoom(db.Model):
    __tablename__ = "educator_rooms"
    __table_args__ = (
        db.UniqueConstraint(
            "educator_id",
            "room_id",
            name="UQ_educator_rooms",
        ),
        {"schema": "dbo"},
    )

    educator_room_id = db.Column(db.Integer, primary_key=True)

    educator_id = db.Column(
        db.Integer,
        db.ForeignKey("dbo.educators.educator_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    room_id = db.Column(
        db.Integer,
        db.ForeignKey("dbo.rooms.room_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    room = db.relationship(
        "Room",
        back_populates="educator_rooms",
        lazy="selectin",
    )
    
    assigned_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.sysutcdatetime(),
    )

    educator = db.relationship("Educator", lazy="selectin")

    room = db.relationship("Room", lazy="selectin")
