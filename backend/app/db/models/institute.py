from sqlalchemy import Float, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import GUID, new_uuid


class Institute(Base):
    __tablename__ = "institutes"

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # shelter/skill_center/ngo/rehab
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=True)
    state: Mapped[str] = mapped_column(String(100), nullable=True)
    compliance_score: Mapped[float] = mapped_column(Numeric(5, 2), default=100.0)
    status: Mapped[str] = mapped_column(String(10), default="green")  # green/yellow/red
    renewal_status: Mapped[str] = mapped_column(String(10), default="pending")  # pending/approved/rejected

    users = relationship("User", back_populates="institute")
    assignments = relationship("Assignment", back_populates="institute")
    alerts = relationship("Alert", back_populates="institute")
