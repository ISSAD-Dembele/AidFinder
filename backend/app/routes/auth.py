from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.securite import get_current_user
from app.models.utilisateurs import Utilisateur

from app.database.session import get_db
from app.schemas.utilisateur import (UserCreate, UserLogin, UserResponse, Token, MessageResponse)

from app.services.auth_service import(register_user, login_user, deactivate_user)

router = APIRouter(
    prefix ="/auth",
    tags =["Authentification"]
)

@router.post("/register", response_model=UserResponse)
def register(
    user:UserCreate,
    db:Session = Depends(get_db)
):
    return register_user(db, user)

@router.post("/login", response_model=Token)
def login(
    user: UserLogin,
    db:Session = Depends(get_db)
):
    return login_user(db, user)

@router.patch("/deactivate", response_model=MessageResponse)
def deactivate(
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return deactivate_user(db, current_user)