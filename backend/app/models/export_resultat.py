from sqlalchemy import Table, Column, Integer, ForeignKey

from app.database.database import Base
export_resultat=Table(
    "export_resultat",
    Base.metadata,
    Column("export_id", Integer, ForeignKey("exports_pdf.export_id"), primary_key=True),
    Column("resultat_id", Integer, ForeignKey("resultats_chatbots.resultat_id"), primary_key=True)
)