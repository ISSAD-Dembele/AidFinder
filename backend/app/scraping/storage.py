from sqlalchemy.orm import Session

from app.models.aides import Aides
from app.database.database import SessionLocal

def get_existing_aide(db: Session, content_hash: str):
    "Recherche une aide existante grace a son content_hash"
    return (
        db.query(Aides).filter(Aides.content_hash == content_hash).first()
    )

def insert_aide(db: Session, data: dict):
    "insere une nouvelle aide dans la base de donnee"
    aide= Aides(**data)
    db.add(aide)
    db.commit()
    db.refresh(aide)
    return aide

def update_aide(db: Session, aide: Aides, data:dict):
    "Met a jour une aide existante"
    for key, value in data.items():
        setattr(aide, key, value)
    db.commit()
    db.refresh(aide)
    return aide

def save_record(db: Session, data: dict):
    "Insère ou met à jour une aide."
    content_hash = data.get("content_hash")
    if not content_hash:
        return None

    existing = get_existing_aide(db, content_hash)
    if existing:
        return update_aide(db, existing, data)

    return insert_aide(db, data)

def save_records(records: list):
    "Sauvegarde une liste d'aides."

    db = SessionLocal()

    try:
        for record in records:
            save_record(db, record)

    finally:
        db.close()