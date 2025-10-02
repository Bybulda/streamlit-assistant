from fastapi import APIRouter, Depends
from backend.app.models.chat import ChatRequest, ChatResponse
from backend.app.services.auth import verify_token

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat(req: ChatRequest, username: str = Depends(verify_token)):
    return {"response": f"({username}) сказал: {req.message}"}
