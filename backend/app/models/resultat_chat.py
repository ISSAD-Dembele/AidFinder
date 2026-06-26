from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .export_resultat import export_resultat
from datetime import datetime
from app.database.database import Base

class ResultatChatbot(Base):
    __tablename__ = "resultats_chatbots"

    resultat_id = Column(Integer, primary_key=True, index=True)
    historique_id = Column(Integer, ForeignKey("historiques.historique_id"), nullable=False)
    aide_id = Column(Integer, ForeignKey("aides.aide_id"), nullable=False)
    score_matching = Column(Integer)
    date_creation = Column(DateTime, default=datetime.utcnow)
    
    #les relations avec les autres tables
    historique = relationship("Historique", back_populates="resultats_chatbots")
    exports_pdf = relationship("ExportPDF", secondary=export_resultat, back_populates="resultats")
    aide = relationship("Aides", back_populates="resultats_chatbots")