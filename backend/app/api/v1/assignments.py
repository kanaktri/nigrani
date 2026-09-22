from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user, require_role
from app.core.time import utcnow
from app.db.base import get_db
from app.db.models.assignment import Assignment
from app.db.models.institute import Institute
from app.db.models.user import User
from app.schemas.assignment import AssignmentOut, GeofencePingRequest
from app.services.assignment_engine import Inspector
from app.services.assignment_engine import Institute as EngineInstitute
from app.services.assignment_engine import select_assignment
from app.services.geofence import is_within_geofence

router = APIRouter(prefix="/api/v1/assignments", tags=["assignments"])


def _build_history(db: Session) -> dict[str, list[str]]:
    """inspector_id -> chronological list of institute_ids inspected, for the fairness constraint."""
    rows = db.query(Assignment).order_by(Assignment.created_at.asc()).all()
    history: dict[str, list[str]] = {}
    for row in rows:
        history.setdefault(str(row.inspector_id), []).append(str(row.institute_id))
    return history


def _days_since_last_inspection(db: Session, institute_id) -> int:
    last = (
        db.query(func.max(Assignment.created_at))
        .filter(Assignment.institute_id == institute_id)
        .scalar()
    )
    if last is None:
        return 30  # never inspected -> treat as heavily overdue
    return max(1, (utcnow() - last).days)


@router.post("/generate", response_model=AssignmentOut, status_code=201)
def generate_assignment(db: Session = Depends(get_db), _user: User = Depends(require_role("admin"))):
    institutes = db.query(Institute).all()
    inspectors = db.query(User).filter(User.role == "inspector").all()

    if not institutes:
        raise HTTPException(status_code=400, detail="No institutes registered")
    if not inspectors:
        raise HTTPException(status_code=400, detail="No inspectors registered")

    engine_institutes = [
        EngineInstitute(id=str(i.id), days_since_last_inspection=_days_since_last_inspection(db, i.id))
        for i in institutes
    ]
    engine_inspectors = [Inspector(id=str(i.id)) for i in inspectors]
    history = _build_history(db)

    result = select_assignment(engine_institutes, engine_inspectors, history, fairness_window=settings.FAIRNESS_WINDOW)

    assignment = Assignment(
        institute_id=result.institute_id,
        inspector_id=result.inspector_id,
        random_seed_ref=result.random_seed_ref,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.get("/mine", response_model=AssignmentOut | None)
def my_assignment(db: Session = Depends(get_db), user: User = Depends(require_role("inspector"))):
    """An inspector can only ever see their OWN latest assignment - never the full schedule."""
    assignment = (
        db.query(Assignment)
        .filter(Assignment.inspector_id == user.id)
        .order_by(Assignment.created_at.desc())
        .first()
    )
    return assignment


@router.post("/{assignment_id}/geofence-ping", response_model=AssignmentOut)
def geofence_ping(
    assignment_id: str,
    payload: GeofencePingRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("inspector")),
):
    assignment = db.get(Assignment, assignment_id)
    if not assignment or str(assignment.inspector_id) != str(user.id):
        raise HTTPException(status_code=404, detail="Assignment not found")

    institute = db.get(Institute, assignment.institute_id)
    if is_within_geofence(payload.latitude, payload.longitude, institute.latitude, institute.longitude, settings.GEOFENCE_RADIUS_METERS):
        now = utcnow()
        assignment.geofence_triggered_at = now
        # This is the only moment the institute learns it's being inspected -
        # the notice window is near-zero by design.
        assignment.notified_institute_at = now
        db.commit()
        db.refresh(assignment)

    return assignment
