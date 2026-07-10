from fastapi import status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.datetime_utils import utc_now
from app.models.utilisateurs import Utilisateur
from app.schemas.utilisateur import UserCreate, UserLogin
from app.core.securite import hash_password, verify_password, create_access_token
from app.core.statuts_compte import (
    ACTIF,
    DESACTIVE_UTILISATEUR,
    est_desactive_par_utilisateur,
    est_suspendu_par_admin,
)


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
    
    # Add the new user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

def login_user(db: Session, user: UserLogin):
    stmt = select(Utilisateur).where(Utilisateur.email == user.email)
    bd_user = db.execute(stmt).scalar_one_or_none()
    if bd_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )

    # Suspension admin : refus immédiat, non contournable à la connexion
    if est_suspendu_par_admin(bd_user.statut_compte):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Votre compte a été suspendu par un administrateur. Contactez le support pour plus d'informations."
        )

    if not verify_password(user.password, bd_user.mot_de_passe_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )

    # Pause volontaire : la connexion réactive automatiquement le compte
    if est_desactive_par_utilisateur(bd_user.statut_compte):
        bd_user.statut_compte = ACTIF
        bd_user.date_desactivation = None

    bd_user.date_derniere_connexion = utc_now()
    db.commit()
    db.refresh(bd_user)

    return _generate_login_response(bd_user)

def deactivate_user(db: Session, current_user: Utilisateur):
    if est_suspendu_par_admin(current_user.statut_compte):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ce compte est suspendu par un administrateur"
        )
    if est_desactive_par_utilisateur(current_user.statut_compte):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce compte est déjà désactivé"
        )

    # Désactivation volontaire — distincte d'une suspension admin
    current_user.statut_compte = DESACTIVE_UTILISATEUR
    current_user.date_desactivation = utc_now()
        
    db.commit()
    db.refresh(current_user)
        
    return {"message": "Compte désactivé avec succès"}
