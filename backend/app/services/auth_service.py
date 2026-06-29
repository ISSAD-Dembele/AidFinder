from datetime import datetime, timezone

from fastapi import status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.utilisateurs import Utilisateur
from app.schemas.utilisateur import UserCreate, UserLogin
from app.core.securite import hash_password, verify_password, create_access_token

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
        statut_compte="actif",  # Default status
        date_creation=datetime.now(timezone.utc)
    )
    
    # Add the new user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

def login_user(db: Session, user: UserLogin):
    # Vérifiez si l'utilisateur existe
    stmt=select(Utilisateur).where(Utilisateur.email == user.email)
    bd_user = db.execute(stmt).scalar_one_or_none()
    if bd_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )
    # Vérifiez le mot de passe
    if not verify_password(user.password, bd_user.mot_de_passe_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )
    access_token= create_access_token(
        data={"sub":str(bd_user.user_id)}
        )
    return {
        "access_token":access_token,
        "token_type":"bearer"
    }