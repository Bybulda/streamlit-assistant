from backend.app.repositories import user_repository, document_repository

def test_create_and_get_document(db_session):
    # Создаём пользователя
    user = user_repository.create_user(db_session, "uploader", "pw")

    # Создаём документ
    doc = document_repository.create_document(db_session, "file.txt", "/path/file.txt", user.id)
    assert doc.id is not None
    assert doc.filename == "file.txt"
    assert doc.owner_id == user.id

    # Получаем документы пользователя
    docs = document_repository.get_documents_by_user(db_session, user.id)
    assert len(docs) == 1
    assert docs[0].filename == "file.txt"

def test_delete_document(db_session):
    user = user_repository.create_user(db_session, "deleter", "pw")
    doc = document_repository.create_document(db_session, "old.txt", "/old.txt", user.id)

    deleted = document_repository.delete_document(db_session, doc.id)
    assert deleted is True

    # Проверим, что удалён
    found = document_repository.get_document_by_id(db_session, doc.id)
    assert found is None
