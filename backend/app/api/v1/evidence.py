from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import require_role
from app.db.base import get_db
from app.db.models.assignment import Assignment
from app.db.models.evidence import Evidence
from app.db.models.user import User
from app.schemas.evidence import EvidenceOut, EvidenceUploadResult
from app.services.hashing import verify_hash
from app.services.storage import get_storage

router = APIRouter(prefix="/api/v1/evidence", tags=["evidence"])


@router.post("/upload", response_model=EvidenceUploadResult)
async def upload_evidence(
    file: UploadFile,
    assignment_id: str = Form(...),
    client_hash: str = Form(..., description="SHA-256 computed on-device at capture time"),
    gps_lat: float = Form(...),
    gps_lng: float = Form(...),
    device_id: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_role("inspector")),
):
    assignment = db.get(Assignment, assignment_id)
    if not assignment or str(assignment.inspector_id) != str(user.id):
        raise HTTPException(status_code=404, detail="Assignment not found")

    contents = await file.read()

    # The single most important check in the whole pipeline: the client's
    # claimed hash must match what the server independently computes from
    # the bytes it actually received. Any mismatch is an instant, outright
    # rejection - never a warning, never a "flagged but accepted".
    matches, server_hash = verify_hash(contents, client_hash)
    if not matches:
        return EvidenceUploadResult(status="REJECTED", reason="hash_mismatch")

    storage = get_storage()
    key = f"{assignment_id}/{server_hash}_{file.filename}"
    file_url = storage.save(key, contents)

    evidence = Evidence(
        assignment_id=assignment_id,
        file_url=file_url,
        sha256_hash=server_hash,
        gps_lat=gps_lat,
        gps_lng=gps_lng,
        device_id=device_id,
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    return EvidenceUploadResult(status="OK", evidence=EvidenceOut.model_validate(evidence))


@router.get("/{assignment_id}", response_model=list[EvidenceOut])
def list_evidence_for_assignment(assignment_id: str, db: Session = Depends(get_db), _user: User = Depends(require_role("official", "admin"))):
    return db.query(Evidence).filter(Evidence.assignment_id == assignment_id).all()
