from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class Historique(Base):
    __tablename__ = "historiques"

    historique_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("utilisateurs.user_id"), nullable=False)
    titre_resume = Column(String, nullable=False)
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_derniere_activite = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    #les relations avec les autres tables
    utilisateur = relationship("Utilisateur", back_populates="historiques")
    discussions = relationship("Discussion", back_populates="historique", cascade="all, delete-orphan")
    resultats_chatbots = relationship("ResultatChatbot", back_populates="historique", cascade="all, delete-orphan")