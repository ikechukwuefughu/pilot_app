from app import db
from sqlalchemy import func


class Branch(db.Model):
    __tablename__ = "branches"
    __table_args__ = {"schema": "dbo"}

    branch_id = db.Column(db.Integer, primary_key=True)

    branch_name = db.Column(db.Unicode(150), nullable=False, index=True)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=func.sysutcdatetime(),
    )

    rooms = db.relationship(
        "Room",
        back_populates="branch",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def to_dict(self):
        return {
            "branch_id": self.branch_id,
            "branch_name": self.branch_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
