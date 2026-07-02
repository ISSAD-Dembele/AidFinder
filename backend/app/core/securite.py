from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from passlib.context import CryptContext #gestionnaire de hashage de mot de passe
from fastapi.security import OAuth2PasswordBearer

from app.core.config import(SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES)
from app.core.statuts_compte import est_desactive_par_utilisateur, est_suspendu_par_admin
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.utilisateurs import Utilisateur
from app.database.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

#notre fonction de création de token d'accès

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token d'accès invalide où expiré."
        )

def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token d'accès invalide ou expiré."
        )
        
    # Récupérer l'utilisateur à partir de la base de données
    
    stmt = select(Utilisateur).where(Utilisateur.user_id == int(user_id))
    user = db.execute(stmt).scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé."
        )

    # Bloque l'accès aux routes protégées si le compte n'est plus actif
    if est_suspendu_par_admin(user.statut_compte):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Votre compte a été suspendu par un administrateur."
        )
    if est_desactive_par_utilisateur(user.statut_compte):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ce compte est désactivé."
        )

    return user