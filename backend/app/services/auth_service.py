from fastapi import status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.datetime_utils import utc_now
from app.models.utilisateurs import Utilisateur
from app.schemas.utilisateur import UserCreate, UserLogin
from app.core.securite import hash_password, verify_password, create_access_token
from app.core.statuts_compte import (
    ACTIF,
    est_suspendu,
)
from app.services.admin_service import reactivate_expired_suspension


def _generate_login_response(user: Utilisateur) -> dict:
    access_token = create_access_token(data={"sub": str(user.user_id)})
    return {"access_token": access_token, "token_type": "bearer"}


def register_user(db: Session, user: UserCreate):
    # Vérifiez si l'utilisateur existe déjà
    stmt=select(Utilisateur).where(Utilisateur.email == user.email)
    existing_user = db.execute(stmt).scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email déjà enregistré"
        )
    # Hash the password
    hashed_password = hash_password(user.password)
    
    # Create a new user instance
    new_user = Utilisateur(
        nom=user.nom,
        email=user.email,
        mot_de_passe_hash=hashed_password,
        role="utilisateur",  # Default role
        statut_compte=ACTIF,
        date_creation=utc_now()
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception:
        db.rollback()
        raise
    
    return new_user

def login_user(db: Session, user: UserLogin):
    stmt = select(Utilisateur).where(Utilisateur.email == user.email)
    bd_user = db.execute(stmt).scalar_one_or_none()
    if bd_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )

    reactivate_expired_suspension(db, bd_user)

    if est_suspendu(bd_user.statut_compte):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Votre compte est suspendu jusqu'à la date de réactivation prévue."
        )

    if not verify_password(user.password, bd_user.mot_de_passe_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )

    try:
        bd_user.date_derniere_connexion = utc_now()
        db.commit()
        db.refresh(bd_user)
    except Exception:
        db.rollback()
        raise

    return _generate_login_response(bd_user)
