from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.base import get_db
from app.db.models.alert import Alert
from app.db.models.user import User
from app.schemas.alert import ALERT_ACTIONS, AlertActionRequest, AlertOut

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertOut])
def list_alerts(
    severity: str | None = Query(default=None),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
    _user: User = Depends(require_role("official", "admin")),
):
    q = db.query(Alert)
    if severity:
        q = q.filter(Alert.severity == severity)
    if status:
        q = q.filter(Alert.status == status)
    return q.order_by(Alert.created_at.desc()).all()


@router.patch("/{alert_id}/action", response_model=AlertOut)
def act_on_alert(
    alert_id: str,
    payload: AlertActionRequest,
    db: Session = Depends(get_db),
    _user: User = Depends(require_role("official")),
):
    if payload.action not in ALERT_ACTIONS:
        raise HTTPException(status_code=422, detail=f"action must be one of {ALERT_ACTIONS}")

    alert = db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = payload.action
    db.commit()
    db.refresh(alert)
    return alert
