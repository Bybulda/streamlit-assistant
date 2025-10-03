from sqlalchemy.orm import Session
from backend.app.models.model import Document

def create_document(db: Session, filename: str, path: str, owner_id: int) -> Document:
    doc = Document(filename=filename, path=path, owner_id=owner_id)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def get_documents_by_user(db: Session, user_id: int) -> list[Document]:
    return db.query(Document).filter(Document.owner_id == user_id).all()

def get_document_by_id(db: Session, doc_id: int) -> Document | None:
    return db.query(Document).filter(Document.id == doc_id).first()

def delete_document(db: Session, doc_id: int) -> bool:
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        return False
    db.delete(doc)
    db.commit()
    return True
