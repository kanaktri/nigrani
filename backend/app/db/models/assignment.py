from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import utcnow
from app.db.base import Base
from app.db.types import GUID, new_uuid


class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=new_uuid)
    institute_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("institutes.id"), nullable=False)
    inspector_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("users.id"), nullable=False)
    random_seed_ref: Mapped[str] = mapped_column(String(64), nullable=False)  # audit reference, never the raw seed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    geofence_triggered_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    notified_institute_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    institute = relationship("Institute", back_populates="assignments")
    inspector = relationship("User")
    evidence = relationship("Evidence", back_populates="assignment")
