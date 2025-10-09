from backend.app.repositories import user_repository

def test_create_and_get_user(db_session):
    # Создаём пользователя
    user = user_repository.create_user(db_session, "alice", "password123")
    assert user.id is not None
    assert user.username == "alice"

    # Получаем по имени
    fetched = user_repository.get_user_by_username(db_session, "alice")
    assert fetched is not None
    assert fetched.username == "alice"

def test_password_verification(db_session):
    user = user_repository.create_user(db_session, "bob", "secret")
    assert user_repository.verify_password("secret", user.hashed_password)
    assert not user_repository.verify_password("wrong", user.hashed_password)
