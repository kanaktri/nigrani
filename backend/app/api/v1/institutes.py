from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.db.base import get_db
from app.db.models.alert import Alert
from app.db.models.institute import Institute
from app.db.models.user import User
from app.schemas.alert import AlertOut
from app.schemas.camera_and_analytics import RenewalDecision
from app.schemas.institute import (INSTITUTE_TYPES, InstituteCreate,
                                   InstituteOut)

router = APIRouter(prefix="/api/v1/institutes", tags=["institutes"])


@router.get("", response_model=list[InstituteOut])
def list_institutes(db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    return db.query(Institute).all()


@router.post("", response_model=InstituteOut, status_code=201)
def create_institute(
    payload: InstituteCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role("admin", "official")),
):
    if payload.type not in INSTITUTE_TYPES:
        raise HTTPException(status_code=422, detail=f"type must be one of {INSTITUTE_TYPES}")

    institute = Institute(**payload.model_dump())
    db.add(institute)
    db.commit()
    db.refresh(institute)
    return institute


@router.get("/{institute_id}/score")
def get_score(institute_id: str, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    institute = db.get(Institute, institute_id)
    if not institute:
        raise HTTPException(status_code=404, detail="Institute not found")
    return {"institute_id": institute_id, "compliance_score": float(institute.compliance_score), "status": institute.status}


@router.patch("/{institute_id}/renewal", response_model=InstituteOut)
def decide_renewal(
    institute_id: str,
    payload: RenewalDecision,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role("official", "admin")),
):
    if payload.decision not in ("approved", "rejected"):
        raise HTTPException(status_code=422, detail="decision must be 'approved' or 'rejected'")

    institute = db.get(Institute, institute_id)
    if not institute:
        raise HTTPException(status_code=404, detail="Institute not found")

    institute.renewal_status = payload.decision
    db.commit()
    db.refresh(institute)
    return institute


@router.get("/{institute_id}/alerts", response_model=list[AlertOut])
def institute_scoped_alerts(
    institute_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Setu's 'view findings for my institute' screen. Unlike /alerts
    (official/admin only, sees everything), this is scoped to one
    institute and open to that institute's own staff/beneficiaries too -
    they need to see findings about themselves to respond to them, but
    never anyone else's.
    """
    if user.role in ("institute_staff", "beneficiary") and str(user.institute_id) != str(institute_id):
        raise HTTPException(status_code=403, detail="You can only view your own institute's findings")
    if user.role not in ("official", "admin", "institute_staff", "beneficiary"):
        raise HTTPException(status_code=403, detail="Not permitted to view findings")

    return (
        db.query(Alert)
        .filter(Alert.institute_id == institute_id)
        .order_by(Alert.created_at.desc())
        .all()
    )
