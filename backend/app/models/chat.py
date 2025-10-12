from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

class ChatRequest(BaseModel):
    document_id: int
    model: str
    message: str

class ChatResponse(BaseModel):
    message: str
    error: Optional[str] = None

class ChatHistoryItem(BaseModel):
    id: int
    document_id: int
    user_id: int
    role: str
    message: str
    model: Optional[str] = None
    created_at: datetime



class ChatHistoryResponse(BaseModel):
    history: List[ChatHistoryItem]