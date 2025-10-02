import os
from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from backend.app.services.auth import verify_token

UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), username: str = Depends(verify_token)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return JSONResponse(content={"message": f"Пользователь {username} загрузил файл {file.filename}"})
