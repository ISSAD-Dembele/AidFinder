from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.database import Base
from app.core.datetime_utils import utc_now

class Historique(Base):
    __tablename__ = "historiques"

    historique_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("utilisateurs.user_id"), nullable=False)
    titre_resume = Column(String, nullable=False)
    date_creation = Column(DateTime(timezone=True), default=utc_now)
    date_derniere_activite = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    conversation_meta = Column(Text, nullable=True)
    
    #les relations avec les autres tables
    utilisateur = relationship("Utilisateur", back_populates="historiques")
    discussions = relationship("Discussion", back_populates="historique", cascade="all, delete-orphan")
    resultats_chatbots = relationship("ResultatChatbot", back_populates="historique", cascade="all, delete-orphan")
