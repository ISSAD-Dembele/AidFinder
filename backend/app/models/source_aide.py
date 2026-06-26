from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database.database import Base

class SourceAide(Base):
    __tablename__ = "sources_aides"

    source_id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    url = Column(String, nullable=False)
    type_source = Column(String)
    est_fiable = Column(Boolean, default=True)
    derniere_collecte = Column(DateTime)
    
    #les relations avec les autres tables
    aides = relationship("Aides", back_populates="source")