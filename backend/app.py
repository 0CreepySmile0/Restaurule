from fastapi import FastAPI, Response, Request, HTTPException, Depends
from backend.db import DBConnector
from backend.repository.session_repo import SessionRepo
from backend.repository.user_repo import UserRepo
from backend.services.auth_service import AuthService

app = FastAPI()
db = DBConnector()
session_repo = SessionRepo(db)
user_repo = UserRepo(db)
auth_service = AuthService(user_repo, session_repo)

@app.post("/login")
def login(response: Response, username: str, password: str):
    session_id = auth_service.login(username, password)

    if session_id is None:
        return {"error": "Invalid login"}

    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        max_age=60 * 60 * 24,
        secure=False,  # True in production (HTTPS)
        samesite="lax"
    )

    return {"message": "Logged in"}

@app.post("/logout")
def logout(request: Request, response: Response):
    session_id = request.cookies.get("session_id")

    if session_id:
        auth_service.logout()

    response.delete_cookie("session_id")

    return {"message": "Logged out"}

def get_current_user(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(401)

    session = auth_service.get_session_by_id(session_id)
    if not session:
        raise HTTPException(401)

    user = auth_service.get_user_by_id(session["user_id"])
    return user
