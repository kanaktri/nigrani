from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.base import get_db
from app.db.models.alert import Alert
from app.db.models.institute import Institute
from app.db.models.user import User
from app.schemas.camera_and_analytics import ComplianceSummary

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/compliance-summary", response_model=ComplianceSummary)
def compliance_summary(db: Session = Depends(get_db), _user: User = Depends(require_role("official", "admin"))):
    """
    The aggregate view a single institute's score can't show: how many
    institutes are in each status bucket, the average score across the
    whole portfolio, and how many alerts are currently open - this is
    what 'cross-institute compliance analytics' actually means, as
    opposed to Sentinel just repeating the map one institute at a time.
    """
    institutes = db.query(Institute).all()
    total = len(institutes)
    avg_score = (sum(float(i.compliance_score) for i in institutes) / total) if total else 0.0

    return ComplianceSummary(
        total_institutes=total,
        average_compliance_score=round(avg_score, 2),
        green_count=sum(1 for i in institutes if i.status == "green"),
        yellow_count=sum(1 for i in institutes if i.status == "yellow"),
        red_count=sum(1 for i in institutes if i.status == "red"),
        open_alerts_count=db.query(func.count(Alert.id)).filter(Alert.status == "open").scalar() or 0,
        red_alerts_count=db.query(func.count(Alert.id)).filter(Alert.severity == "red", Alert.status == "open").scalar() or 0,
    )
