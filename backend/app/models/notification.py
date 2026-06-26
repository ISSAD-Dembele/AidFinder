from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("utilisateurs.user_id"), nullable=False)
    titre = Column(String, nullable=False)
    message = Column(String, nullable=False)
    lu = Column(Boolean, default=False)
    date_creation = Column(DateTime, default=datetime.utcnow)
    
    utilisateur = relationship("Utilisateur", back_populates="notifications")