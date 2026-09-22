from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.types import GUID, new_uuid

# Kept as plain strings (not a DB enum) so new roles never require a migration -
# validated instead at the Pydantic schema layer.
ROLES = ("admin", "institute_staff", "inspector", "official", "beneficiary")


class User(Base):
    __tablename__ = "users"

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False)
    aadhaar_ekyc_ref: Mapped[str] = mapped_column(String(255), nullable=True)  # reference token only, never raw Aadhaar
    institute_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("institutes.id"), nullable=True)

    institute = relationship("Institute", back_populates="users")
