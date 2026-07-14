from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.datetime_utils import utc_now
from app.database.database import Base

class ActionModeration(Base):
    __tablename__ = "actions_moderations"

    action_id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("administrateurs.admin_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("utilisateurs.user_id"), nullable=False)
    type_action = Column(String, nullable=False)  # avertissement | suspension | reactivation_automatique
    motif = Column(Text, nullable=False)
    message_affiche = Column(String)
    message_conversation = Column(Text, nullable=True)
    date_creation = Column(DateTime(timezone=True), default=utc_now)
    
    #les relations avec les autres tables
    administrateur = relationship("Administrateur", back_populates="actions_moderation")
    utilisateur = relationship("Utilisateur", back_populates="actions_moderation")
