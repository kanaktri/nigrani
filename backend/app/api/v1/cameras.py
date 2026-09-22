from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.base import get_db
from app.db.models.camera_feed import CameraFeed
from app.db.models.user import User
from app.schemas.camera_and_analytics import CameraFeedOut

router = APIRouter(prefix="/api/v1", tags=["cameras"])


@router.get("/cameras", response_model=list[CameraFeedOut])
def list_all_cameras(db: Session = Depends(get_db), _user: User = Depends(require_role("official", "admin"))):
    """The cross-institute camera wall Sentinel's stakeholders need -
    every camera across every institute in one view, not one institute
    at a time."""
    return db.query(CameraFeed).all()


@router.get("/institutes/{institute_id}/cameras", response_model=list[CameraFeedOut])
def list_institute_cameras(
    institute_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("official", "admin", "institute_staff")),
):
    if user.role == "institute_staff" and str(user.institute_id) != str(institute_id):
        raise HTTPException(status_code=403, detail="You can only view your own institute's cameras")
    return db.query(CameraFeed).filter(CameraFeed.institute_id == institute_id).all()
