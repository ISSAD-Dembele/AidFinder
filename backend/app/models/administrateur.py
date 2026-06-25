from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.database import Base

class Administrateur(Base):
    __tablename__="administrateurs"
    admin_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("utilisateurs.user_id"))
    niveau_acces = Column(String, nullable=False)