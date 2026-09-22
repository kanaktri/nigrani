from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import utcnow
from app.db.base import Base
from app.db.types import GUID, new_uuid


class VCCall(Base):
    __tablename__ = "vc_calls"

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=new_uuid)
    institute_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("institutes.id"), nullable=False)
    beneficiary_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("users.id"), nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    picked_up_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    recording_ref: Mapped[str] = mapped_column(String(255), nullable=True)

    institute = relationship("Institute")
    beneficiary = relationship("User")
