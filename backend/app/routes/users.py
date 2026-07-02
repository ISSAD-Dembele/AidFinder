from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.securite import get_current_user
from app.models.utilisateurs import Utilisateur

from app.schemas.utilisateur import (UserProfileUpdate, ChangePassword, UserProfileResponse, MessageResponse)
from app.services.user_service import( update_user_profile, change_user_password, get_user_profile)

router = APIRouter(
    prefix="/users",
    tags=["Utilisateurs"],
)
# consulter son porfil
@router.get("/me", response_model=UserProfileResponse)
def read_profile(current_user: Utilisateur = Depends(get_current_user)):
    return get_user_profile(current_user)

#modifier son profil
@router.patch("/me", response_model=UserProfileResponse)
def update_profile(data: UserProfileUpdate, current_user: Utilisateur = Depends(get_current_user), db: Session = Depends(get_db)):
    return update_user_profile(db, current_user, data)

#changer son mot de passe
@router.patch("/change-password", response_model=MessageResponse)
def change_password(data: ChangePassword, current_user: Utilisateur = Depends(get_current_user), db: Session = Depends(get_db)):
    return change_user_password(db, current_user, data)