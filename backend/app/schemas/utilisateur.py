from datetime import datetime
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
    
class UserReponse(BaseModel):
    user_id: int
    nom: str
    email: EmailStr
    role: str
    statut_compte: str
    date_naissance: datetime | None=None
    date_creation: datetime
    model_config = ConfigDict(from_attributes=True)
    
class Token(BaseModel):
    access_token: str
    token_type: str