import pathlib

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from streamlit import status

from backend.ai.chroma import chroma_service
from backend.ai.chroma.chroma_service import search_similar_chunks
from backend.ai.file_utils import file_loader
from backend.ai.llm.llm_factory import get_llm_client
from backend.app.core.database import get_db
from backend.app.models import model
from backend.app.models.chat import ChatRequest, ChatResponse, ChatHistoryResponse
from backend.app.repositories import chat_repository, document_repository
from backend.app.services.auth import verify_token

router = APIRouter()

@router.post("/")
async def chat(req: ChatRequest, username: str = Depends(verify_token)):
    return {"response": f"({username}) сказал: {req.message}"}


@router.get("/chat/history", response_model=ChatHistoryResponse)
async def get_chat_history(document_id: int, username: str = Depends(verify_token), db: Session = Depends(get_db)):
    messages_history = chat_repository.get_messages_by_document(db, document_id)
    return {"history": messages_history}


@router.post("/chat/request", response_model=ChatResponse)
async def get_chat_request(request: ChatRequest, username: str = Depends(verify_token), db: Session = Depends(get_db)):
    # 1. проверить наличие документа в бд, если нет - ошибка
    # 2. проверить наличия документа в хрома, если нет - добавить и сделать вектора
    # 3. сохранить запрос в бд
    # 4. отправить запрос в ии вместе с векторами
    # 5. получить ответ, сохранить в бд, в зависимости от ответа напечатать ошибку или без ошибки
    document = document_repository.get_document_by_id(db, request.document_id)
    user = db.query(model.User).filter(model.User.username == username).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not chroma_service.document_exists(str(request.document_id)):
        if not chroma_service.document_exists(str(request.document_id)):
            file_suffix = pathlib.Path(document.filename).suffix
            document_content = file_loader.extract_text_from_bytes(document.content, file_suffix)
            metadata = {
                "document_id": str(request.document_id),
                "filename": document.filename,
                "file_type": file_suffix
            }
            chroma_service.add_full_document(str(request.document_id), document_content, metadata, request.model)
        chat_repository.add_message(db, request.document_id, "user", request.message)
    chunks = search_similar_chunks(request.message, 5, str(request.document_id))
    llm_model = get_llm_client(request.model, request, chunks)
    response = llm_model.send()
    return {"message": response}