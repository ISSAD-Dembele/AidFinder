from sqlalchemy import Column, Integer, String, ForeignKey,Text, DateTime
from sqlalchemy.orm import relationship
from app.database.database import Base
from app.core.datetime_utils import utc_now

class Discussion(Base):
    __tablename__ = "discussions"

    discussion_id = Column(Integer, primary_key=True, index=True)
    historique_id = Column(Integer, ForeignKey("historiques.historique_id"), nullable=False)
    expediteur = Column(String, nullable=False)
    contenu = Column(Text, nullable=False)
    date_creation = Column(DateTime(timezone=True), default=utc_now)
    
    #les relations avec les autres tables
    historique = relationship("Historique", back_populates="discussions")
