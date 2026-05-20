# app/models/household.py
from app import db
from sqlalchemy import func

class Household(db.Model):
    __tablename__ = "household"
    __table_args__ = {"schema": "dbo"}  # maps to dbo.household

    household_id = db.Column(db.Integer, primary_key=True)

    created_at = db.Column(
        db.DateTime,                       # DATETIME2(0)
        nullable=False,
        server_default=func.sysutcdatetime(),  # matches DEFAULT SYSUTCDATETIME()
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    household_name = db.Column(db.Unicode(200), nullable=False)
    address_line1  = db.Column(db.Unicode(200), nullable=False)
    address_line2  = db.Column(db.Unicode(200))
    city           = db.Column(db.Unicode(100), nullable=False)
    county         = db.Column(db.Unicode(100))
    eircode        = db.Column(db.String(7))      # CHAR(7)
    phone          = db.Column(db.Unicode(20))

    # Relationship to Parent
    parents = db.relationship(
        "Parent",
        back_populates="household",
        cascade="all, delete-orphan",
        passive_deletes=True,  # respects ON DELETE CASCADE on FK
        lazy="selectin",
    )
