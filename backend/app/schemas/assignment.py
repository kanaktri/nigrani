from datetime import datetime

from pydantic import BaseModel


class AssignmentOut(BaseModel):
    id: str
    institute_id: str
    inspector_id: str
    random_seed_ref: str
    created_at: datetime
    geofence_triggered_at: datetime | None
    notified_institute_at: datetime | None

    model_config = {"from_attributes": True}


class GeofencePingRequest(BaseModel):
    latitude: float
    longitude: float
