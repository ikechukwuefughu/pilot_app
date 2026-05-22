from app import db
from sqlalchemy import func

class EducatorWorkingHour(db.Model):
    __tablename__ = "educator_working_hours"
    __table_args__ = {"schema": "dbo"}

    working_hour_id = db.Column(db.Integer, primary_key=True)

    educator_id = db.Column(
        db.Integer,
        db.ForeignKey("dbo.educators.educator_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    day_of_week = db.Column(
        db.Unicode(20),
        nullable=False,
        index=True,
    )

    start_time = db.Column(db.Time, nullable=False)

    end_time = db.Column(db.Time, nullable=False)

    educator = db.relationship("Educator", lazy="selectin")
