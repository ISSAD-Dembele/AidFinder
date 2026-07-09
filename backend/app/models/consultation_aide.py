from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database.database import Base


class ConsultationAide(Base):
    __tablename__ = "consultations_aides"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("utilisateurs.user_id"), nullable=False, index=True)
    aide_id = Column(Integer, ForeignKey("aides.aide_id"), nullable=False, index=True)
    date_consultation = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    utilisateur = relationship("Utilisateur", back_populates="consultations_aides")
    aide = relationship("Aides", back_populates="consultations")
