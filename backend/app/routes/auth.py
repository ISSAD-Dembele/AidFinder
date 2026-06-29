from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.utilisateur import (UserCreate, UserLogin, UserReponse, Token)

from app.services.auth_service import(register_user, login_user)

router = APIRouter(
    prefix ="/auth",
    tag =["Authentification"]
)

@router.post("/register", reponse_model=UserReponse)
def register(
    user:UserCreate,
    db:Session = Depends(get_db)
):
    return register_user(db, user)

@router.post("/login", reponse_model=Token)
def login(
    user: UserLogin,
    db:Session = Depends(get_db)
):
    return login_user(db, user)