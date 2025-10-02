from fastapi import APIRouter, HTTPException
from backend.app.models.user import UserLogin, TokenResponse
from backend.app.services.auth import create_access_token

router = APIRouter()


fake_users = {
    "admin": "123",
    "user": "pass"
}

@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin):
    if fake_users.get(user.username) == user.password:
        token = create_access_token({"sub": user.username})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid username or password")
