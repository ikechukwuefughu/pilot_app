from app import db
from sqlalchemy import func

class Parent(db.Model):
    __tablename__ = "parent"
    __table_args__ = {"schema": "dbo"}  # maps to dbo.parent

    parent_id = db.Column(db.Integer, primary_key=True)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.sysutcdatetime(),  # DEFAULT SYSUTCDATETIME()
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    household_id = db.Column(
        db.Integer,
        db.ForeignKey("dbo.household.household_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,  # IX_parent_household_id equivalent
    )

    first_name = db.Column(db.Unicode(100), nullable=False)
    last_name  = db.Column(db.Unicode(100), nullable=False)
    phone      = db.Column(db.Unicode(20))
    email      = db.Column(db.Unicode(254))
    is_primary = db.Column(
        db.Boolean,
        nullable=False,
        server_default=db.text("0"),  # BIT with DEFAULT(0)
    )

    household = db.relationship("Household", back_populates="parents")
