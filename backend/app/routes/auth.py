from fastapi import APIRouter

router = APIRouter()

@router.post("/login")
def login(username: str, password: str):
    # TODO: добавить нормальную авторизацию
    if username == "admin" and password == "123":
        return {"token": "fake-jwt-token"}
    return {"error": "invalid credentials"}
