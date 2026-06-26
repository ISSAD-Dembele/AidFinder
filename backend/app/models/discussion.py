from sqlalchemy import Column, Integer, String, ForeignKey,Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class Discussion(Base):
    __tablename__ = "discussions"

    discussion_id = Column(Integer, primary_key=True, index=True)
    historique_id = Column(Integer, ForeignKey("historiques.historique_id"), nullable=False)
    expediteur = Column(String, nullable=False)
    contenu = Column(Text, nullable=False)
    date_creation = Column(DateTime, default=datetime.utcnow)
    
    #les relations avec les autres tables
    historique = relationship("Historique", back_populates="discussions")