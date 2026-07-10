from datetime import date, datetime, timezone

from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.datetime_utils import as_utc
from app.models.aides import Aides
from app.models.consultation_aide import ConsultationAide
from app.models.discussion import Discussion
from app.models.export_pdf import ExportPDF
from app.models.historique import Historique
from app.models.resultat_chat import ResultatChatbot
from app.models.utilisateurs import Utilisateur


PROFILE_FIELDS = (
    "nom",
    "date_naissance",
    "ville",
    "region",
    "niveau_etude",
    "statut_socio_pro",
    "situation_handicap",
    "photo_profil",
)


def calculate_profile_progress(user: Utilisateur) -> int:
    completed = 0
    for field in PROFILE_FIELDS:
        value = getattr(user, field, None)
        if value is not None and value != "":
            completed += 1
    return round((completed / len(PROFILE_FIELDS)) * 100)


def _serialize_aid(
    aide: Aides,
    score_matching: int | None = None,
    raisons: list[str] | None = None,
    date_consultation=None,
) -> dict:
    categorie = aide.categorie.nom if aide.categorie else aide.type_aide
    return {
        "id": aide.aide_id,
        "aide_id": aide.aide_id,
        "titre": aide.titre,
        "description": aide.description,
        "image": aide.image_url,
        "image_url": aide.image_url,
        "categorie": categorie,
        "url_officielle": aide.url_officielle,
        "region_cible": aide.region_cible,
        "type_aide": aide.type_aide,
        "score_matching": score_matching,
        "compatibilite": score_matching,
        "raisons": raisons or [],
        "date_creation": as_utc(aide.date_creation),
        "date_consultation": as_utc(date_consultation),
    }


def record_aid_consultation(db: Session, user: Utilisateur, aide_id: int) -> ConsultationAide:
    aide_exists = db.query(Aides.aide_id).filter(Aides.aide_id == aide_id).first()
    if aide_exists is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aide introuvable.",
        )

    consultation = ConsultationAide(user_id=user.user_id, aide_id=aide_id)
    try:
        db.add(consultation)
        db.commit()
        db.refresh(consultation)
    except Exception:
        db.rollback()
        raise
    return consultation


def record_and_get_consulted_aid(db: Session, user: Utilisateur, aide_id: int) -> dict:
    consultation = record_aid_consultation(db, user, aide_id)
    aide = db.query(Aides).filter(Aides.aide_id == aide_id).one()
    return _serialize_aid(aide, date_consultation=consultation.date_consultation)


def get_user_stats(db: Session, user: Utilisateur) -> dict:
    nombre_recherches = db.query(func.count(Historique.historique_id)).filter(
        Historique.user_id == user.user_id
    ).scalar() or 0
    nombre_conversations = db.query(func.count(Historique.historique_id)).filter(
        Historique.user_id == user.user_id
    ).scalar() or 0
    nombre_recommandations = count_user_recommendations(db, user, limit=10)
    nombre_pdf_exportes = db.query(func.count(ExportPDF.export_id)).filter(
        ExportPDF.user_id == user.user_id
    ).scalar() or 0

    return {
        "nombre_recherches": nombre_recherches,
        "nombre_recommandations": nombre_recommandations,
        "nombre_pdf_exportes": nombre_pdf_exportes,
        "nombre_conversations": nombre_conversations,
        "progression_profil": calculate_profile_progress(user),
    }


def get_user_history(db: Session, user: Utilisateur) -> list[dict]:
    histories = (
        db.query(
            Historique.historique_id,
            Historique.titre_resume,
            Historique.date_creation,
            Historique.date_derniere_activite,
            func.count(func.distinct(Discussion.discussion_id)).label("nombre_messages"),
            func.count(func.distinct(ResultatChatbot.resultat_id)).label("nombre_recommandations"),
        )
        .outerjoin(Discussion, Discussion.historique_id == Historique.historique_id)
        .outerjoin(ResultatChatbot, ResultatChatbot.historique_id == Historique.historique_id)
        .filter(Historique.user_id == user.user_id)
        .group_by(
            Historique.historique_id,
            Historique.titre_resume,
            Historique.date_creation,
            Historique.date_derniere_activite,
        )
        .order_by(desc(Historique.date_derniere_activite), desc(Historique.historique_id))
        .all()
    )

    return [
        {
            "historique_id": history.historique_id,
            "titre_resume": history.titre_resume,
            "nombre_messages": history.nombre_messages,
            "nombre_recommandations": history.nombre_recommandations,
            "dernier_message": db.query(Discussion.contenu)
                .filter(Discussion.historique_id == history.historique_id)
                .order_by(desc(Discussion.date_creation), desc(Discussion.discussion_id))
                .limit(1).scalar(),
            "date_creation": as_utc(history.date_creation),
            "date_derniere_activite": as_utc(history.date_derniere_activite),
        }
        for history in histories
    ]


def get_recent_conversations(db: Session, user: Utilisateur, limit: int = 5) -> list[dict]:
    histories = (
        db.query(Historique)
        .filter(Historique.user_id == user.user_id)
        .order_by(desc(Historique.date_derniere_activite), desc(Historique.historique_id))
        .limit(limit)
        .all()
    )

    conversations = []
    for history in histories:
        last_message = (
            db.query(Discussion)
            .filter(Discussion.historique_id == history.historique_id)
            .order_by(desc(Discussion.date_creation), desc(Discussion.discussion_id))
            .first()
        )
        conversations.append(
            {
                "historique_id": history.historique_id,
                "titre_resume": history.titre_resume,
                "dernier_message": last_message.contenu if last_message else None,
                "date_creation": as_utc(history.date_creation),
                "date_derniere_activite": as_utc(history.date_derniere_activite),
            }
        )

    return conversations


def get_recent_aids(db: Session, user: Utilisateur, limit: int = 5) -> list[dict]:
    rows = (
        db.query(Aides, ConsultationAide.date_consultation)
        .join(ConsultationAide, ConsultationAide.aide_id == Aides.aide_id)
        .filter(ConsultationAide.user_id == user.user_id)
        .order_by(desc(ConsultationAide.date_consultation), desc(ConsultationAide.id))
        .limit(limit)
        .all()
    )
    return [_serialize_aid(aide, date_consultation=date_consultation) for aide, date_consultation in rows]


def _normalize(value: str | None) -> str:
    return (value or "").strip().casefold()


def _is_open_requirement(value: str | None) -> bool:
    normalized = _normalize(value)
    return not normalized or any(token in normalized for token in ("tous", "toutes", "maroc", "national"))


def _matches_requirement(requirement: str | None, *profile_values: str | None) -> bool:
    if _is_open_requirement(requirement):
        return True
    normalized_requirement = _normalize(requirement)
    return any(_normalize(value) and _normalize(value) in normalized_requirement for value in profile_values)


def _calculate_age(date_naissance: date | None) -> int | None:
    if date_naissance is None:
        return None
    today = date.today()
    return today.year - date_naissance.year - ((today.month, today.day) < (date_naissance.month, date_naissance.day))


def calculate_recommendation_score(user: Utilisateur, aide: Aides) -> tuple[int, list[str]]:
    score = 0
    raisons: list[str] = []
    user_age = _calculate_age(user.date_naissance)
    ville = getattr(user, "ville", None)

    if _matches_requirement(aide.region_cible, ville, user.region):
        score += 25
        raisons.append("Région compatible" if not _is_open_requirement(aide.region_cible) else "Région non restrictive")
    else:
        raisons.append("Région non compatible")

    if _matches_requirement(aide.niveau_etude_requis, user.niveau_etude):
        score += 20
        raisons.append("Niveau d'étude compatible" if not _is_open_requirement(aide.niveau_etude_requis) else "Niveau d'étude non restrictif")
    else:
        raisons.append("Niveau d'étude non compatible")

    if _matches_requirement(aide.statut_socio_pro_requis, user.statut_socio_pro):
        score += 20
        raisons.append("Statut compatible" if not _is_open_requirement(aide.statut_socio_pro_requis) else "Statut non restrictif")
    else:
        raisons.append("Statut non compatible")

    age_min = aide.age_min
    age_max = aide.age_max
    if age_min is None and age_max is None:
        score += 20
        raisons.append("Âge non limité")
    elif user_age is None:
        raisons.append("Âge non renseigné")
    elif (age_min is None or user_age >= age_min) and (age_max is None or user_age <= age_max):
        score += 20
        raisons.append("Âge compatible")
    else:
        raisons.append("Âge non compatible")

    if aide.handicap_requis is True:
        if user.situation_handicap is True:
            score += 15
            raisons.append("Handicap compatible")
        else:
            raisons.append("Handicap requis")
    else:
        score += 15
        raisons.append("Handicap non requis")

    return min(100, max(0, score)), raisons


def _recommendation_rows(db: Session, user: Utilisateur) -> list[tuple[Aides, int, list[str]]]:
    aides = (
        db.query(Aides)
        .filter(Aides.est_active.is_(True))
        .order_by(desc(Aides.date_creation), desc(Aides.aide_id))
        .all()
    )
    rows = []
    for aide in aides:
        score, raisons = calculate_recommendation_score(user, aide)
        rows.append((aide, score, raisons))
    return sorted(
        rows,
        key=lambda row: (
            row[1],
            as_utc(row[0].date_creation) or datetime.min.replace(tzinfo=timezone.utc),
            row[0].aide_id,
        ),
        reverse=True,
    )


def get_user_recommendations(db: Session, user: Utilisateur, limit: int = 10) -> list[dict]:
    rows = _recommendation_rows(db, user)[:limit]
    return [_serialize_aid(aide, score, raisons) for aide, score, raisons in rows]


def count_user_recommendations(db: Session, user: Utilisateur, limit: int = 10) -> int:
    return len(_recommendation_rows(db, user)[:limit])


def get_user_dashboard(db: Session, user: Utilisateur) -> dict:
    stats = get_user_stats(db, user)
    recommendations = get_user_recommendations(db, user, limit=5)
    return {
        "nom_utilisateur": user.nom,
        "photo": user.photo_profil,
        "progression_profil": stats["progression_profil"],
        "nombre_recherches": stats["nombre_recherches"],
        "nombre_recommandations": stats["nombre_recommandations"],
        "nombre_pdf_exportes": stats["nombre_pdf_exportes"],
        "nombre_conversations": stats["nombre_conversations"],
        "dernieres_aides_consultees": get_recent_aids(db, user),
        "dernieres_conversations": get_recent_conversations(db, user),
        "aides_recommandees": recommendations,
    }
