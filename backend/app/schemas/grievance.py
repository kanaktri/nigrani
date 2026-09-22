from datetime import datetime

from pydantic import BaseModel, Field

from app.db.models.grievance import GRIEVANCE_STATUSES


class GrievanceCreate(BaseModel):
    institute_id: str
    subject: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=5)


class GrievanceOut(BaseModel):
    id: str
    institute_id: str
    submitted_by_id: str
    subject: str
    description: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class GrievanceStatusUpdate(BaseModel):
    status: str = Field(description=f"One of {GRIEVANCE_STATUSES}")
