from fastapi import HTTPException, status
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.core.datetime_utils import as_utc, utc_now
from app.core.statuts_compte import ACTIF, DESACTIVE_UTILISATEUR, SUSPENDU_ADMIN
from app.models.aides import Aides
from app.models.categorie_aide import CategorieAide
from app.models.consultation_aide import ConsultationAide
from app.models.discussion import Discussion
from app.models.export_pdf import ExportPDF
from app.models.historique import Historique
from app.models.scraping_logs import ScrapingLog
from app.models.source_aide import SourceAide
from app.models.utilisateurs import Utilisateur
from app.schemas.admin import AdminAideCreate, AdminAideUpdate, AdminUserUpdate
from app.scraping.manager import run_all_scrapers


VALID_ROLES = {"utilisateur", "administrateur"}
VALID_STATUSES = {ACTIF, DESACTIVE_UTILISATEUR, SUSPENDU_ADMIN}


def _get_user_or_404(db: Session, user_id: int) -> Utilisateur:
    user = db.query(Utilisateur).filter(Utilisateur.user_id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable.")
    return user


def _get_aide_or_404(db: Session, aide_id: int) -> Aides:
    aide = db.query(Aides).filter(Aides.aide_id == aide_id).first()
    if aide is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aide introuvable.")
    return aide


def _get_source_or_404(db: Session, source_id: int) -> SourceAide:
    source = db.query(SourceAide).filter(SourceAide.source_id == source_id).first()
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source introuvable.")
    return source


def _ensure_relations_exist(db: Session, source_id: int | None, categorie_id: int | None) -> None:
    if source_id is not None:
        exists = db.query(SourceAide.source_id).filter(SourceAide.source_id == source_id).first()
        if exists is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Source inexistante.")
    if categorie_id is not None:
        exists = db.query(CategorieAide.categorie_id).filter(CategorieAide.categorie_id == categorie_id).first()
        if exists is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Catégorie inexistante.")


def _serialize_aide(aide: Aides) -> dict:
    return {
        "aide_id": aide.aide_id,
        "source_id": aide.source_id,
        "categorie_id": aide.categorie_id,
        "titre": aide.titre,
        "description": aide.description,
        "date_limite": aide.date_limite,
        "type_aide": aide.type_aide,
        "montant": aide.montant,
        "age_min": aide.age_min,
        "age_max": aide.age_max,
        "region_cible": aide.region_cible,
        "niveau_etude_requis": aide.niveau_etude_requis,
        "statut_socio_pro_requis": aide.statut_socio_pro_requis,
        "handicap_requis": aide.handicap_requis,
        "url_officielle": aide.url_officielle,
        "image_url": aide.image_url,
        "est_active": aide.est_active,
        "categorie": aide.categorie.nom if aide.categorie else None,
        "source": aide.source.nom if aide.source else None,
        "date_creation": as_utc(aide.date_creation),
        "derniere_mise_a_jour": as_utc(aide.derniere_mise_a_jour),
    }


def get_dashboard_stats(db: Session) -> dict:
    return {
        "total_utilisateurs": db.query(func.count(Utilisateur.user_id)).scalar() or 0,
        "total_aides": db.query(func.count(Aides.aide_id)).scalar() or 0,
        "total_categories": db.query(func.count(CategorieAide.categorie_id)).scalar() or 0,
        "total_sources": db.query(func.count(SourceAide.source_id)).scalar() or 0,
        "total_conversations": db.query(func.count(Discussion.discussion_id)).scalar() or 0,
        "total_pdf_exportes": db.query(func.count(ExportPDF.export_id)).scalar() or 0,
        "comptes_actifs": db.query(func.count(Utilisateur.user_id)).filter(Utilisateur.statut_compte == ACTIF).scalar() or 0,
        "comptes_desactives": db.query(func.count(Utilisateur.user_id)).filter(Utilisateur.statut_compte != ACTIF).scalar() or 0,
    }


def list_users(db: Session) -> list[Utilisateur]:
    return db.query(Utilisateur).order_by(desc(Utilisateur.date_creation), desc(Utilisateur.user_id)).all()


def get_user(db: Session, user_id: int) -> Utilisateur:
    return _get_user_or_404(db, user_id)


def update_user(db: Session, user_id: int, data: AdminUserUpdate) -> Utilisateur:
    user = _get_user_or_404(db, user_id)
    values = data.model_dump(exclude_unset=True)
    if values.get("role") and values["role"] not in VALID_ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rôle invalide.")
    if values.get("statut_compte") and values["statut_compte"] not in VALID_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Statut de compte invalide.")
    try:
        for key, value in values.items():
            setattr(user, key, value)
        if values.get("statut_compte") == ACTIF:
            user.date_desactivation = None
        elif values.get("statut_compte") in {DESACTIVE_UTILISATEUR, SUSPENDU_ADMIN}:
            user.date_desactivation = utc_now()
        db.commit()
        db.refresh(user)
        return user
    except Exception:
        db.rollback()
        raise


def activate_user(db: Session, user_id: int) -> Utilisateur:
    user = _get_user_or_404(db, user_id)
    try:
        user.statut_compte = ACTIF
        user.date_desactivation = None
        db.commit()
        db.refresh(user)
        return user
    except Exception:
        db.rollback()
        raise


def deactivate_user(db: Session, user_id: int) -> Utilisateur:
    user = _get_user_or_404(db, user_id)
    try:
        user.statut_compte = SUSPENDU_ADMIN
        user.date_desactivation = utc_now()
        db.commit()
        db.refresh(user)
        return user
    except Exception:
        db.rollback()
        raise


def delete_user(db: Session, user_id: int) -> dict:
    user = _get_user_or_404(db, user_id)
    try:
        db.delete(user)
        db.commit()
        return {"message": "Utilisateur supprimé avec succès."}
    except Exception:
        db.rollback()
        raise


def list_aides(db: Session) -> list[dict]:
    aides = db.query(Aides).order_by(desc(Aides.date_creation), desc(Aides.aide_id)).all()
    return [_serialize_aide(aide) for aide in aides]


def create_aide(db: Session, data: AdminAideCreate) -> dict:
    _ensure_relations_exist(db, data.source_id, data.categorie_id)
    try:
        aide = Aides(**data.model_dump(), derniere_mise_a_jour=utc_now())
        db.add(aide)
        db.commit()
        db.refresh(aide)
        return _serialize_aide(aide)
    except Exception:
        db.rollback()
        raise


def update_aide(db: Session, aide_id: int, data: AdminAideUpdate) -> dict:
    aide = _get_aide_or_404(db, aide_id)
    values = data.model_dump(exclude_unset=True)
    _ensure_relations_exist(db, values.get("source_id"), values.get("categorie_id"))
    try:
        for key, value in values.items():
            setattr(aide, key, value)
        aide.derniere_mise_a_jour = utc_now()
        db.commit()
        db.refresh(aide)
        return _serialize_aide(aide)
    except Exception:
        db.rollback()
        raise


def delete_aide(db: Session, aide_id: int) -> dict:
    aide = _get_aide_or_404(db, aide_id)
    try:
        db.delete(aide)
        db.commit()
        return {"message": "Aide supprimée avec succès."}
    except Exception:
        db.rollback()
        raise


def set_aide_active(db: Session, aide_id: int, active: bool) -> dict:
    aide = _get_aide_or_404(db, aide_id)
    try:
        aide.est_active = active
        aide.derniere_mise_a_jour = utc_now()
        db.commit()
        db.refresh(aide)
        return _serialize_aide(aide)
    except Exception:
        db.rollback()
        raise


def list_sources(db: Session) -> list[dict]:
    rows = (
        db.query(
            SourceAide,
            func.count(Aides.aide_id).label("nombre_aides"),
            func.max(ScrapingLog.finished_at).label("dernier_scraping"),
        )
        .outerjoin(Aides, Aides.source_id == SourceAide.source_id)
        .outerjoin(ScrapingLog, ScrapingLog.source == SourceAide.nom)
        .group_by(
            SourceAide.source_id,
            SourceAide.nom,
            SourceAide.url,
            SourceAide.type_source,
            SourceAide.est_fiable,
            SourceAide.derniere_collecte,
        )
        .order_by(SourceAide.nom)
        .all()
    )
    results = []
    for source, nombre_aides, dernier_scraping in rows:
        last_log = (
            db.query(ScrapingLog)
            .filter(ScrapingLog.source == source.nom)
            .order_by(desc(ScrapingLog.finished_at), desc(ScrapingLog.scraplogs_id))
            .first()
        )
        results.append(
            {
                "source_id": source.source_id,
                "nom": source.nom,
                "url": source.url,
                "type_source": source.type_source,
                "est_fiable": source.est_fiable,
                "fiabilite": "fiable" if source.est_fiable else "à vérifier",
                "nombre_aides": nombre_aides or 0,
                "dernier_scraping": dernier_scraping or source.derniere_collecte,
                "statut": last_log.status if last_log else "jamais_scrape",
            }
        )
    return results


def rerun_source_scraping(db: Session, source_id: int) -> dict:
    source = _get_source_or_404(db, source_id)
    try:
        records = run_all_scrapers()
        source.derniere_collecte = utc_now()
        db.commit()
        db.refresh(source)
        return {
            "message": "Scraping relancé avec succès.",
            "source_id": source.source_id,
            "source": source.nom,
            "records": len(records),
            "dernier_scraping": source.derniere_collecte,
        }
    except Exception:
        db.rollback()
        raise


def get_statistics(db: Session) -> dict:
    aides_par_categorie = [
        {"label": label or "Sans catégorie", "total": total or 0}
        for label, total in (
            db.query(CategorieAide.nom, func.count(Aides.aide_id))
            .outerjoin(Aides, Aides.categorie_id == CategorieAide.categorie_id)
            .group_by(CategorieAide.nom)
            .order_by(CategorieAide.nom)
            .all()
        )
    ]
    aides_par_region = [
        {"label": label or "Non renseignée", "total": total or 0}
        for label, total in (
            db.query(Aides.region_cible, func.count(Aides.aide_id))
            .group_by(Aides.region_cible)
            .order_by(desc(func.count(Aides.aide_id)))
            .all()
        )
    ]
    evolution_utilisateurs = [
        {"date": created_date, "total": total or 0}
        for created_date, total in (
            db.query(func.date(Utilisateur.date_creation), func.count(Utilisateur.user_id))
            .filter(Utilisateur.date_creation.isnot(None))
            .group_by(func.date(Utilisateur.date_creation))
            .order_by(func.date(Utilisateur.date_creation))
            .all()
        )
    ]
    evolution_conversations = [
        {"date": created_date, "total": total or 0}
        for created_date, total in (
            db.query(func.date(Discussion.date_creation), func.count(Discussion.discussion_id))
            .filter(Discussion.date_creation.isnot(None))
            .group_by(func.date(Discussion.date_creation))
            .order_by(func.date(Discussion.date_creation))
            .all()
        )
    ]
    evolution_exports_pdf = [
        {"date": created_date, "total": total or 0}
        for created_date, total in (
            db.query(func.date(ExportPDF.date_creation), func.count(ExportPDF.export_id))
            .filter(ExportPDF.date_creation.isnot(None))
            .group_by(func.date(ExportPDF.date_creation))
            .order_by(func.date(ExportPDF.date_creation))
            .all()
        )
    ]
    sources_les_plus_utilisees = [
        {"label": label or "Source inconnue", "total": total or 0}
        for label, total in (
            db.query(SourceAide.nom, func.count(ConsultationAide.id))
            .join(Aides, Aides.source_id == SourceAide.source_id)
            .join(ConsultationAide, ConsultationAide.aide_id == Aides.aide_id)
            .group_by(SourceAide.nom)
            .order_by(desc(func.count(ConsultationAide.id)))
            .limit(10)
            .all()
        )
    ]
    return {
        "aides_par_categorie": aides_par_categorie,
        "aides_par_region": aides_par_region,
        "evolution_utilisateurs": evolution_utilisateurs,
        "evolution_conversations": evolution_conversations,
        "evolution_exports_pdf": evolution_exports_pdf,
        "sources_les_plus_utilisees": sources_les_plus_utilisees,
    }


def get_logs(db: Session) -> dict:
    derniers_scrapes = db.query(ScrapingLog).order_by(desc(ScrapingLog.created_at), desc(ScrapingLog.scraplogs_id)).limit(10).all()
    dernieres_erreurs = (
        db.query(ScrapingLog)
        .filter(ScrapingLog.error_message.isnot(None))
        .order_by(desc(ScrapingLog.created_at), desc(ScrapingLog.scraplogs_id))
        .limit(10)
        .all()
    )
    users = (
        db.query(Utilisateur)
        .filter(Utilisateur.date_derniere_connexion.isnot(None))
        .order_by(desc(Utilisateur.date_derniere_connexion), desc(Utilisateur.user_id))
        .limit(10)
        .all()
    )
    return {
        "derniers_scrapes": derniers_scrapes,
        "dernieres_erreurs": dernieres_erreurs,
        "dernieres_connexions": [
            {
                "user_id": user.user_id,
                "nom": user.nom,
                "email": user.email,
                "role": user.role,
                "date_derniere_connexion": as_utc(user.date_derniere_connexion),
            }
            for user in users
        ],
    }
