from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.core.time import utcnow
from app.db.base import get_db
from app.db.models.user import User
from app.db.models.vc_call import VCCall

router = APIRouter(prefix="/api/v1/vc", tags=["vc"])


class VCTriggerRequest(BaseModel):
    institute_id: str
    beneficiary_id: str


class VCStatusRequest(BaseModel):
    picked_up: bool


class VCCallOut(BaseModel):
    id: str
    institute_id: str
    beneficiary_id: str
    triggered_at: datetime
    picked_up_at: datetime | None

    model_config = {"from_attributes": True}


@router.post("/trigger", response_model=VCCallOut, status_code=201)
def trigger_call(payload: VCTriggerRequest, db: Session = Depends(get_db), _user: User = Depends(require_role("admin"))):
    """
    Places a call to a random beneficiary. In this build the actual WebRTC
    dial-out is a documented integration point (see README - Jitsi setup);
    what's real here is the row that records the call was placed, when,
    and to whom - which is what the 2-minute pickup window and vc_miss
    alert logic key off.
    """
    call = VCCall(institute_id=payload.institute_id, beneficiary_id=payload.beneficiary_id)
    db.add(call)
    db.commit()
    db.refresh(call)
    return call


@router.patch("/{call_id}/status", response_model=VCCallOut)
def update_status(call_id: str, payload: VCStatusRequest, db: Session = Depends(get_db), _user: User = Depends(require_role("admin"))):
    call = db.get(VCCall, call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    if payload.picked_up:
        call.picked_up_at = utcnow()
    db.commit()
    db.refresh(call)
    return call
