# Streamlit Assistant

Веб-приложение для загрузки документов, поиска по ним с помощью ChromaDB и получения ответов от LLM (OpenAI / OpenRouter). Состоит из backend (FastAPI) и frontend (Streamlit).

---

## Структура проекта (ключевые файлы)
```
streamlit_assistant/
├── docker-compose.yaml
├── .env.example
├── README.md
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── documents.py
│   │   │   └── chat.py
│   │   ├── services/
│   │   │   └── auth.py
│   │   ├── models/
│   │   │   ├── model.py
│   │   │   └── chat.py
│   │   ├── repositories/
│   │   │   ├── user_repository.py
│   │   │   ├── document_repository.py
│   │   │   └── chat_repository.py
│   └── ai/
│       ├── chroma/
│       │   └── chroma_service.py
│       ├── llm/
│       │   ├── llm_factory.py
│       │   └── impl/
│       │       ├── chat_gpt_model.py
│       │       └── mistral_model.py
│       └── file_utils/
│           └── file_loader.py
└── streamlit/
    ├── app.py
    ├── Dockerfile
    └── pages/
        ├── auth_page.py
        ├── documents_page.py
        └── analyze_page.py
```

---

## Что делает проект (вкратце)
1. Backend хранит пользователей, документы и историю чата в Postgres (SQLAlchemy + Alembic).
2. Документы можно загружать через API; содержимое хранится в базе и извлекается для векторизации.
3. При первом запросе по документу содержимое разбивается на чанки, добавляется в ChromaDB и индексируется.
4. По запросу пользователя ищутся наиболее релевантные чанки, формируется prompt и отправляется в выбранную LLM (OpenAI или OpenRouter/Mistral).
5. Ответ сохраняется в истории чата и возвращается пользователю.
6. Frontend (Streamlit) предоставляет UI для авторизации, загрузки документов и чат-интерфейса.

---

## Основные эндпоинты API

- GET /  
  Обычный health-check. Обработчик: [`backend.app.main.root`](backend/app/main.py) ([backend/app/main.py](backend/app/main.py))

- POST /auth/register  
  Регистрация пользователя. Обработчик: [`backend.app.routes.auth.register`](backend/app/routes/auth.py) ([backend/app/routes/auth.py])  
  Параметры: username, password

- POST /auth/login  
  Авторизация (OAuth2 password form). Обработчик: [`backend.app.routes.auth.login`](backend/app/routes/auth.py) ([backend/app/routes/auth.py])  
  Возвращает: { "access_token": "...", "token_type": "bearer" }

- POST /documents/upload  
  Загрузить файл. Авторизация требуется (Bearer). Обработчик: [`backend.app.routes.documents.upload_document`](backend/app/routes/documents.py) ([backend/app/routes/documents.py])  
  Поле: file (multipart/form-data)

- GET /documents/my  
  Получить список загруженных пользователем документов. Обработчик: [`backend.app.routes.documents.list_user_documents`](backend/app/routes/documents.py) ([backend/app/routes/documents.py])

- DELETE /documents/{doc_id}  
  Удалить документ пользователя. Обработчик: [`backend.app.routes.documents.delete_user_document`](backend/app/routes/documents.py) ([backend/app/routes/documents.py])

- GET /documents/{doc_id}/download  
  Скачать байты документа. Обработчик: [`backend.app.routes.documents.get_user_document`](backend/app/routes/documents.py) ([backend/app/routes/documents.py])

- POST /chat/chat/request  
  Основной запрос для анализа/чата по документу. Обработчик: [`backend.app.routes.chat.get_chat_request`](backend/app/routes/chat.py) ([backend/app/routes/chat.py])  
  Тело: { "document_id": int, "model": str, "message": str } (см. [`backend.app.models.chat.ChatRequest`](backend/app/models/chat.py))

- GET /chat/chat/history?document_id=...  
  Вернуть историю чата для документа. Обработчик: [`backend.app.routes.chat.get_chat_history`](backend/app/routes/chat.py) ([backend/app/routes/chat.py])

---

## Как запустить локально (рекомендуемый способ)
1. Установлен Docker и docker-compose.
2. Запустить все сервисы:
```sh
docker-compose up --build
```
Это поднимет: Postgres, ChromaDB, backend (FastAPI) и frontend (Streamlit). Конфигурация в [docker-compose.yaml](docker-compose.yaml).

---

## Примечания по безопасности
- Токены JWT создаются функцией [`backend.app.services.auth.create_access_token`](backend/app/services/auth.py) и проверяются [`backend.app.services.auth.verify_token`](backend/app/services/auth.py).

---

## Пример .env (НЕ коммитить реальные ключи)
```env
# filepath: .env.example
# Backend / Auth
SECRET_KEY=your_jwt_secret_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database (used locally when not in docker)
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/streamlit_backend

# Chroma
CHROMA_HOST=localhost
CHROMA_PORT=8001
CHROMA_COLLECTION=documents

# OpenAI / OpenRouter keys
OPEN_AI_API_KEY=sk-xxxx-your-openai-key
OPEN_ROUTER_API_KEY=sk-xxxx-your-openrouter-key
OPEN_ROUTER_URL=https://openrouter.ai/api/v1


```

