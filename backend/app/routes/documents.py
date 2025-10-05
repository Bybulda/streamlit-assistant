from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from backend.app.services.auth import verify_token
from backend.app.core.database import get_db
from backend.app.repositories import document_repository
from backend.app.models import model

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

