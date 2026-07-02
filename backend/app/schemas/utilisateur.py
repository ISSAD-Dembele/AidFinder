from datetime import datetime, date
from pydantic import BaseModel, EmailStr, ConfigDict

class UserCreate(BaseModel):
    
    nom: str
    email: EmailStr
    password: str
    
class UserLogin(BaseModel):
    
    email: EmailStr
    password: str

class MessageResponse(BaseModel):
    message: str
    
class UserProfileUpdate(BaseModel):
    nom: str | None = None
    date_naissance: date | None = None
    region: str | None = None
    niveau_etude: str | None = None
    statut_socio_pro: str | None = None
    situation_handicap: bool | None = None
    photo_profil: str | None = None

class UserProfileResponse(BaseModel):
    user_id: int
    nom: str
    email: EmailStr
    role: str
    statut_compte: str
    
    date_naissance: date | None = None
    region: str | None = None
    niveau_etude: str | None = None
    statut_socio_pro: str | None = None
    situation_handicap: bool | None = None
    photo_profil: str | None = None
    date_creation: datetime
    model_config = ConfigDict(from_attributes=True)

class ChangePassword(BaseModel):
    current_password: str
    new_password: str
    confirm_new_password: str
    
class UserResponse(BaseModel):
    user_id: int
    nom: str
    email: EmailStr
    role: str
    statut_compte: str
    date_naissance: date | None=None
    date_creation: datetime
    model_config = ConfigDict(from_attributes=True)
    
class Token(BaseModel):
    access_token: str
    token_type: str
    