from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.db.base import get_db
from app.db.models.grievance import GRIEVANCE_STATUSES, Grievance
from app.db.models.user import User
from app.schemas.grievance import GrievanceCreate, GrievanceOut, GrievanceStatusUpdate

router = APIRouter(prefix="/api/v1/grievances", tags=["grievances"])


@router.post("", response_model=GrievanceOut, status_code=201)
def submit_grievance(
    payload: GrievanceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("institute_staff", "beneficiary")),
):
    # A grievance can only ever be filed against the submitter's OWN
    # institute - never on behalf of another institute they have no
    # connection to.
    if str(user.institute_id) != str(payload.institute_id):
        raise HTTPException(status_code=403, detail="You can only submit a grievance for your own institute")

    grievance = Grievance(
        institute_id=payload.institute_id,
        submitted_by_id=user.id,
        subject=payload.subject,
        description=payload.description,
    )
    db.add(grievance)
    db.commit()
    db.refresh(grievance)
    return grievance


@router.get("", response_model=list[GrievanceOut])
def list_grievances(
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Grievance)
    if user.role in ("official", "admin"):
        pass  # can see every institute's grievances
    elif user.role in ("institute_staff", "beneficiary"):
        q = q.filter(Grievance.institute_id == user.institute_id)  # own institute only, regardless of query params
    else:
        raise HTTPException(status_code=403, detail="Not permitted to view grievances")

    if status:
        q = q.filter(Grievance.status == status)
    return q.order_by(Grievance.created_at.desc()).all()


@router.patch("/{grievance_id}/status", response_model=GrievanceOut)
def update_grievance_status(
    grievance_id: str,
    payload: GrievanceStatusUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role("official")),
):
    if payload.status not in GRIEVANCE_STATUSES:
        raise HTTPException(status_code=422, detail=f"status must be one of {GRIEVANCE_STATUSES}")

    grievance = db.get(Grievance, grievance_id)
    if not grievance:
        raise HTTPException(status_code=404, detail="Grievance not found")

    grievance.status = payload.status
    db.commit()
    db.refresh(grievance)
    return grievance
