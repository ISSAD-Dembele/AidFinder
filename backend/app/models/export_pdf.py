from sqlalchemy import Column, Integer, String, DateTime,ForeignKey
from sqlalchemy.orm import relationship
from .export_resultat import export_resultat
from app.core.datetime_utils import utc_now
from app.database.database import Base

class ExportPDF(Base):
    __tablename__ = "exports_pdf"

    export_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("utilisateurs.user_id"), nullable=False)
    nom_fichier = Column(String, nullable=False)
    date_creation = Column(DateTime(timezone=True), default=utc_now)

    #les relations avec les autres tables
    utilisateur = relationship("Utilisateur", back_populates="exports_pdf")
    resultats = relationship("ResultatChatbot", secondary=export_resultat, back_populates="exports_pdf")
