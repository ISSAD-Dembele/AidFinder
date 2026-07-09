from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session

from app.models.aides import Aides
from app.models.discussion import Discussion
from app.models.export_pdf import ExportPDF
from app.models.historique import Historique
from app.models.resultat_chat import ResultatChatbot
from app.models.utilisateurs import Utilisateur


PROFILE_FIELDS = (
    "nom",
    "date_naissance",
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


def _serialize_aid(aide: Aides, score_matching: int | None = None) -> dict:
    return {
        "aide_id": aide.aide_id,
        "titre": aide.titre,
        "description": aide.description,
        "image_url": aide.image_url,
        "url_officielle": aide.url_officielle,
        "region_cible": aide.region_cible,
        "type_aide": aide.type_aide,
        "score_matching": score_matching,
        "date_creation": aide.date_creation,
    }


def get_user_stats(db: Session, user: Utilisateur) -> dict:
    historique_ids = db.query(Historique.historique_id).filter(Historique.user_id == user.user_id)
    nombre_recherches = db.query(func.count(Historique.historique_id)).filter(
        Historique.user_id == user.user_id
    ).scalar() or 0
    nombre_conversations = db.query(func.count(Discussion.discussion_id)).filter(
        Discussion.historique_id.in_(historique_ids)
    ).scalar() or 0
    nombre_recommandations = db.query(func.count(ResultatChatbot.resultat_id)).filter(
        ResultatChatbot.historique_id.in_(historique_ids)
    ).scalar() or 0
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
            "date_creation": history.date_creation,
            "date_derniere_activite": history.date_derniere_activite,
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
                "date_creation": history.date_creation,
                "date_derniere_activite": history.date_derniere_activite,
            }
        )

    return conversations


def get_recent_aids(db: Session, user: Utilisateur, limit: int = 5) -> list[dict]:
    last_seen = func.max(ResultatChatbot.date_creation).label("last_seen")
    rows = (
        db.query(Aides, last_seen)
        .join(ResultatChatbot, ResultatChatbot.aide_id == Aides.aide_id)
        .join(Historique, Historique.historique_id == ResultatChatbot.historique_id)
        .filter(Historique.user_id == user.user_id)
        .group_by(Aides.aide_id)
        .order_by(desc(last_seen), desc(Aides.aide_id))
        .limit(limit)
        .all()
    )
    return [_serialize_aid(aide) for aide, _ in rows]


def _profile_match_filter(user: Utilisateur):
    filters = []
    if user.region:
        filters.append(
            or_(
                Aides.region_cible.is_(None),
                Aides.region_cible.ilike("%Maroc%"),
                Aides.region_cible.ilike(f"%{user.region}%"),
            )
        )
    if user.niveau_etude:
        filters.append(
            or_(
                Aides.niveau_etude_requis.is_(None),
                Aides.niveau_etude_requis.ilike("%Tous%"),
                Aides.niveau_etude_requis.ilike(f"%{user.niveau_etude}%"),
            )
        )
    if user.statut_socio_pro:
        filters.append(
            or_(
                Aides.statut_socio_pro_requis.is_(None),
                Aides.statut_socio_pro_requis.ilike(f"%{user.statut_socio_pro}%"),
            )
        )
    if user.situation_handicap is not None:
        filters.append(or_(Aides.handicap_requis.is_(False), Aides.handicap_requis == user.situation_handicap))
    return filters


def get_user_recommendations(db: Session, user: Utilisateur, limit: int = 10) -> list[dict]:
    best_score = func.max(ResultatChatbot.score_matching).label("score_matching")
    rows = (
        db.query(Aides, best_score)
        .join(ResultatChatbot, ResultatChatbot.aide_id == Aides.aide_id)
        .join(Historique, Historique.historique_id == ResultatChatbot.historique_id)
        .filter(Historique.user_id == user.user_id)
        .group_by(Aides.aide_id)
        .order_by(desc(best_score), desc(Aides.date_creation), desc(Aides.aide_id))
        .limit(limit)
        .all()
    )
    if rows:
        return [_serialize_aid(aide, score_matching) for aide, score_matching in rows]

    query = db.query(Aides)
    for filter_clause in _profile_match_filter(user):
        query = query.filter(filter_clause)

    aids = (
        query.order_by(desc(Aides.date_creation), desc(Aides.aide_id))
        .limit(limit)
        .all()
    )
    return [_serialize_aid(aide) for aide in aids]


def get_user_dashboard(db: Session, user: Utilisateur) -> dict:
    stats = get_user_stats(db, user)
    return {
        "nom_utilisateur": user.nom,
        "photo": user.photo_profil,
        "progression_profil": stats["progression_profil"],
        "nombre_recherches": stats["nombre_recherches"],
        "nombre_recommandations": stats["nombre_recommandations"],
        "nombre_pdf_exportes": stats["nombre_pdf_exportes"],
        "dernieres_aides_consultees": get_recent_aids(db, user),
        "dernieres_conversations": get_recent_conversations(db, user),
        "dernieres_recommandations_ia": get_user_recommendations(db, user, limit=5),
    }
