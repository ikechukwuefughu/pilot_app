from app import db
from sqlalchemy import func

class ChildContract(db.Model):
    __tablename__ = "child_contracts"
    __table_args__ = {"schema": "dbo"}

    contract_id = db.Column(db.Integer, primary_key=True)

    child_id = db.Column(
        db.Integer,
        db.ForeignKey("dbo.child.child_id", ondelete="CASCADE"),
        index=True
    )

    contract_type = db.Column(db.Unicode(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    agreed_hours_per_week = db.Column(db.Float)
    hourly_rate = db.Column(db.Float)
    subsidy_rate = db.Column(db.Float)

    status = db.Column(db.Unicode(50))

    def to_dict(self):
        return {
            "contract_id": self.contract_id,
            "child_id": self.child_id,
            "contract_type": self.contract_type,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "agreed_hours_per_week": self.agreed_hours_per_week,
            "hourly_rate": self.hourly_rate,
            "subsidy_rate": self.subsidy_rate,
            "status": self.status
        }
