from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class DocumentRequis(Base):
    __tablename__ = "documents_requis"

    document_id = Column(Integer, primary_key=True, index=True)
    aide_id = Column(Integer, ForeignKey("aides.aide_id"), nullable=False)
    nom = Column(String, nullable=False)
    description = Column(Text)

#les relations avec les autres tables
    aide = relationship("Aides", back_populates="documents_requis")