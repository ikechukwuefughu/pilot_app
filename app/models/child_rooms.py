from app import db
from sqlalchemy import func


class ChildRoom(db.Model):
    __tablename__ = "child_rooms"
    __table_args__ = {"schema": "dbo"}

    child_room_id = db.Column(db.Integer, primary_key=True)

    child_id = db.Column(
        db.Integer,
        db.ForeignKey("dbo.child.child_id"),
        nullable=False,
        index=True,
    )

    room_id = db.Column(
        db.Integer,
        db.ForeignKey("dbo.rooms.room_id"),
        nullable=False,
        index=True,
    )

    start_date = db.Column(
        db.Date,
        nullable=False,
        server_default=func.current_date(),
    )

    end_date = db.Column(db.Date)

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        server_default=db.text("1"),
        index=True,
    )

    child = db.relationship("Child", lazy="selectin")
    room = db.relationship("Room", back_populates="child_rooms")
    # room = db.relationship("Room", lazy="selectin")
