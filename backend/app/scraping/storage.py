from sqlalchemy.orm import Session
from datetime import datetime

from app.models.aides import Aides
from app.models.categorie_aide import CategorieAide
from app.models.source_aide import SourceAide
from app.database.database import SessionLocal

DEFAULT_IMAGE_URL = "https://anapec.ma/assets/img/logo.png"


def get_existing_aide(db: Session, content_hash: str):
    "Recherche une aide existante grace a son content_hash"
    return (
        db.query(Aides).filter(Aides.content_hash == content_hash).first()
    )


def get_or_create_source(db: Session, data: dict) -> SourceAide:
    "Retourne une source existante ou la crée."
    source_url = data.get("source_url") or data.get("url_officielle")
    source_nom = data.get("source_nom") or "Source inconnue"

    source = None
    if source_url:
        source = db.query(SourceAide).filter(SourceAide.url == source_url).first()
    if source is None:
        source = db.query(SourceAide).filter(SourceAide.nom == source_nom).first()

    now = datetime.utcnow()
    if source is None:
        source = SourceAide(
            nom=source_nom,
            url=source_url,
            type_source=data.get("source_type"),
            est_fiable=data.get("source_fiable", True),
            derniere_collecte=now,
        )
        db.add(source)
        db.flush()
    else:
        source.derniere_collecte = now
        if data.get("source_type"):
            source.type_source = data["source_type"]
        source.est_fiable = data.get("source_fiable", source.est_fiable)

    return source


def get_or_create_category(db: Session, data: dict) -> CategorieAide:
    "Retourne une catégorie existante ou la crée."
    category_name = data.get("categorie_nom") or data.get("type_aide") or "Autres aides"
    category = db.query(CategorieAide).filter(CategorieAide.nom == category_name).first()
    if category is None:
        category = CategorieAide(
            nom=category_name,
            description=data.get("categorie_description"),
        )
        db.add(category)
        db.flush()
    elif data.get("categorie_description") and not category.description:
        category.description = data["categorie_description"]

    return category


def prepare_aide_data(db: Session, data: dict) -> dict | None:
    "Valide et enrichit une aide avant insertion."
    if not data.get("content_hash") or not data.get("titre") or not data.get("url_officielle"):
        return None

    data["image_url"] = data.get("image_url") or DEFAULT_IMAGE_URL
    source = get_or_create_source(db, data)
    category = get_or_create_category(db, data)

    allowed_fields = {column.name for column in Aides.__table__.columns}
    aide_data = {key: value for key, value in data.items() if key in allowed_fields}
    aide_data["source_id"] = source.source_id
    aide_data["categorie_id"] = category.categorie_id
    aide_data["derniere_mise_a_jour"] = datetime.utcnow()

    return aide_data


def insert_aide(db: Session, data: dict):
    "insere une nouvelle aide dans la base de donnee"
    aide= Aides(**data)
    db.add(aide)
    db.flush()
    return aide

def update_aide(db: Session, aide: Aides, data:dict):
    "Met a jour une aide existante"
    for key, value in data.items():
        setattr(aide, key, value)
    db.flush()
    return aide

def save_record(db: Session, data: dict):
    "Insère ou met à jour une aide."
    prepared_data = prepare_aide_data(db, data)
    if prepared_data is None:
        return None

    content_hash = prepared_data.get("content_hash")
    if not content_hash:
        return None

    existing = get_existing_aide(db, content_hash)
    if existing:
        return update_aide(db, existing, prepared_data)

    return insert_aide(db, prepared_data)

def save_records(records: list):
    "Sauvegarde une liste d'aides."

    db = SessionLocal()

    try:
        for record in records:
            save_record(db, record)
        db.commit()
    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
