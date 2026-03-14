from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.db.models import Document
from app.schemas.document import DocumentResponse
from app.services.storage_service import StorageService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    storage_service = StorageService()
    stored_name, _, size_bytes = storage_service.save_file(file)

    document = Document(
        original_name=file.filename,
        stored_name=stored_name,
        content_type=file.content_type,
        size_bytes=size_bytes,
        status="uploaded"
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


@router.get("/", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    documents = db.execute(
        select(Document).order_by(Document.created_at.desc())
    ).scalars().all()

    return documents