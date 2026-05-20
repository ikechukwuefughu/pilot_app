from app import db
from sqlalchemy import func

class Child(db.Model):
    __tablename__ = "child"
    __table_args__ = {"schema": "dbo"}

    child_id = db.Column(db.Integer, primary_key=True)

    created_at = db.Column(
        db.DateTime,
        server_default=func.sysutcdatetime(),
        nullable=False
    )

    household_id = db.Column(
        db.Integer,
        db.ForeignKey("dbo.household.household_id"),
        nullable=False,
        index=True
    )

    first_name = db.Column(db.Unicode(100), nullable=False)
    last_name = db.Column(db.Unicode(100), nullable=False)

    date_of_birth = db.Column(db.Date)
    ppsn = db.Column(db.Unicode(50))

    ecce_eligible = db.Column(
        db.Boolean,
        server_default=db.text("0"),
        nullable=False
    )

    start_date = db.Column(db.Date)

    chick_code = db.Column(db.Unicode(100), unique=True)

    # relationships
    household = db.relationship("Household", back_populates="children")
    attendance = db.relationship("ChildAttendance", back_populates="child", cascade="all, delete")
