from sqlalchemy.orm import Session
from app.models.utilisateurs import Utilisateur
from app.schemas.utilisateur import (UserProfileUpdate, ChangePassword)
from app.core.securite import verify_password, hash_password
from fastapi import HTTPException, status

def get_user_profile(current_user: Utilisateur):
    return current_user

def update_user_profile(db: Session, current_user: Utilisateur, data: UserProfileUpdate):
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)
        
    db.commit()
    db.refresh(current_user)
    
    return current_user

def change_user_password(db: Session, current_user: Utilisateur, data: ChangePassword):
    if not verify_password(data.current_password, current_user.mot_de_passe_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le mot de passe actuel est incorrect."
        )
    
    if data.new_password != data.confirm_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nouveau mot de passe et la confirmation ne correspondent pas."
        )
    if verify_password(data.new_password, current_user.mot_de_passe_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nouveau mot de passe ne peut pas être le même que l'ancien."
        )
    
    current_user.mot_de_passe_hash = hash_password(data.new_password)
    db.commit()
    db.refresh(current_user)
    
    return {"message": "Mot de passe mis à jour avec succès."}