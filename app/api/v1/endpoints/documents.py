from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
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


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str, db: Session = Depends(get_db)):
    # Busca o documento pelo ID. Se não existir, retorna 404.
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")
    return document


@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: str, db: Session = Depends(get_db)):
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Primeiro apaga do disco, depois do banco.
    # Se invertêssemos a ordem e o disco falhasse, o banco ficaria inconsistente.
    StorageService().delete_file(document.stored_name)
    db.delete(document)
    db.commit()


@router.get("/{document_id}/download")
def download_document(document_id: str, db: Session = Depends(get_db)):
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")

    file_path = StorageService().get_file_path(document.stored_name)

    # FileResponse serve o arquivo diretamente.
    # filename= define o nome que o usuário vê ao baixar.
    return FileResponse(
        path=file_path,
        media_type=document.content_type,
        filename=document.original_name
    )