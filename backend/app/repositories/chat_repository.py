from sqlalchemy.orm import Session
from backend.app.models.model import ChatMessage
from datetime import datetime
from typing import List

def add_message(db: Session, document_id: int, role: str, message: str, model: str = None) -> ChatMessage:
    msg = ChatMessage(
        document_id=document_id,
        role=role,
        message=message,
        model=model,
        created_at=datetime.utcnow()
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_messages_by_document(db: Session, document_id: int) -> List[ChatMessage]:
    return db.query(ChatMessage).filter(ChatMessage.document_id == document_id).order_by(ChatMessage.created_at).all()


def delete_messages_for_document(db: Session, document_id: int):
    db.query(ChatMessage).filter(ChatMessage.document_id == document_id).delete()
    db.commit()

