from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database.database import Base
from app.core.datetime_utils import utc_now

class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("utilisateurs.user_id"), nullable=False)
    titre = Column(String, nullable=False)
    message = Column(String, nullable=False)
    lu = Column(Boolean, default=False)
    date_creation = Column(DateTime(timezone=True), default=utc_now)
    
    utilisateur = relationship("Utilisateur", back_populates="notifications")
