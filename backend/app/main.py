from fastapi import FastAPI
from backend.app.routes import auth, documents, chat

app = FastAPI(title="AI Knowledge Assistant API")


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])

@app.get("/")
def root():
    return {"message": "AI Knowledge Assistant API is running"}

