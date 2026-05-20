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
