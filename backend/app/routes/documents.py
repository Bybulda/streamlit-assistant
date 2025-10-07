import io
import urllib

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models import model
from backend.app.repositories import document_repository
from backend.app.services.auth import verify_token

router = APIRouter()


@router.post("/upload")
async def upload_document(
        file: UploadFile = File(...),
        username: str = Depends(verify_token),
        db: Session = Depends(get_db),
):
    user = db.query(model.User).filter(model.User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    content = await file.read()
    document_repository.create_document(db, file.filename, content, user.id)
    return JSONResponse(content={"message": f"Файл {file.filename} успешно загружен"})


@router.get("/my")
def list_user_documents(
        username: str = Depends(verify_token),
        db: Session = Depends(get_db),
):
    user = db.query(model.User).filter(model.User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    docs = document_repository.get_documents_by_user(db, user.id)
    return [{"id": d.id, "filename": d.filename, "uploaded_at": d.uploaded_at} for d in docs]


@router.delete("/{doc_id}")
def delete_user_document(
        doc_id: int,
        username: str = Depends(verify_token),
        db: Session = Depends(get_db),
):
    user = db.query(model.User).filter(model.User.username == username).first()
    document = document_repository.get_document_by_id(db, doc_id)
    if not document or document.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    document_repository.delete_document(db, doc_id)
    return JSONResponse(content={"message": "Документ успешно удалён"})


@router.get("/{doc_id}/download")
def get_user_document(
        doc_id: int,
        username: str = Depends(verify_token),
        db: Session = Depends(get_db),
):
    user = db.query(model.User).filter(model.User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    document = document_repository.get_document_by_id(db, doc_id)
    if not document or document.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    encoded_filename = urllib.parse.quote(document.filename)


    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
    }

    return StreamingResponse(
        io.BytesIO(document.content),
        media_type="application/octet-stream",
        headers=headers
    )
