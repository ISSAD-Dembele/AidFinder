from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database.database import Base

class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    user_id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    mot_de_passe_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    statut_compte = Column(String, nullable=False)  # actif | desactive_utilisateur | suspendu_admin
    date_naissance = Column(DateTime)
    region = Column(String)
    niveau_etude = Column(String)
    statut_socio_pro = Column(String)
    situation_handicap = Column(Boolean, default=False)
    date_creation = Column(DateTime)
    date_desactivation = Column(DateTime, nullable=True)
    
    #les relations avec les autres tables
    historiques = relationship("Historique", back_populates="utilisateur", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="utilisateur", cascade="all, delete-orphan")
    
    actions_moderation = relationship("ActionModeration", back_populates="utilisateur")
    administrateur = relationship("Administrateur", back_populates="utilisateur", uselist=False)
    exports_pdf = relationship("ExportPDF", back_populates="utilisateur")