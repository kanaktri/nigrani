from pydantic import BaseModel, Field

INSTITUTE_TYPES = ("shelter", "skill_center", "ngo", "rehab")


class InstituteCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    type: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    district: str | None = None
    state: str | None = None


class InstituteOut(BaseModel):
    id: str
    name: str
    type: str
    latitude: float
    longitude: float
    district: str | None
    state: str | None
    compliance_score: float
    status: str
    renewal_status: str

    model_config = {"from_attributes": True}
