from sqlalchemy import Column, Integer, String
from app.database.database import Base

class CategorieAide(Base):
    __tablename__ = "categories_aides"

    categorie_id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    description = Column(String)