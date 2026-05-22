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

    # Relationship to Child
    # 🔥 THIS IS REQUIRED (missing right now)
    children = db.relationship(
        "Child",
        back_populates="household",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def to_dict(self):
        return {
            "household_id": self.household_id,
            "household_name": self.household_name,
            "address_line1": self.address_line1,
            "address_line2": self.address_line2,
            "city": self.city,
            "county": self.county,
            "eircode": self.eircode,
            "phone": self.phone,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
