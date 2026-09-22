from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_role
from app.db.base import get_db
from app.db.models.institute_document import InstituteDocument
from app.db.models.user import User
from app.schemas.institute_document import InstituteDocumentOut
from app.services.storage import get_storage

router = APIRouter(prefix="/api/v1/institutes", tags=["institute-documents"])


@router.post("/{institute_id}/documents", response_model=InstituteDocumentOut, status_code=201)
async def upload_document(
    institute_id: str,
    file: UploadFile,
    description: str | None = Form(default=None),
    alert_id: str | None = Form(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(require_role("institute_staff")),
):
    if str(user.institute_id) != str(institute_id):
        raise HTTPException(status_code=403, detail="You can only upload documents for your own institute")

    contents = await file.read()
    storage = get_storage()
    key = f"institute-documents/{institute_id}/{file.filename}"
    file_url = storage.save(key, contents)

    doc = InstituteDocument(
        institute_id=institute_id,
        alert_id=alert_id,
        uploaded_by_id=user.id,
        file_url=file_url,
        description=description,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/{institute_id}/documents", response_model=list[InstituteDocumentOut])
def list_documents(
    institute_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role in ("institute_staff", "beneficiary") and str(user.institute_id) != str(institute_id):
        raise HTTPException(status_code=403, detail="You can only view your own institute's documents")
    if user.role not in ("official", "admin", "institute_staff", "beneficiary"):
        raise HTTPException(status_code=403, detail="Not permitted to view documents")

    return (
        db.query(InstituteDocument)
        .filter(InstituteDocument.institute_id == institute_id)
        .order_by(InstituteDocument.uploaded_at.desc())
        .all()
    )
