from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class Administrateur(Base):
    __tablename__="administrateurs"
    admin_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("utilisateurs.user_id"), unique=True)
    niveau_acces = Column(String, nullable=False)
    
    #les relations avec les autres tables
    utilisateur = relationship("Utilisateur", back_populates="administrateur")
    actions_moderation = relationship("ActionModeration", back_populates="administrateur")