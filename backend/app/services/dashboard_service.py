from sqlalchemy import and_, case, desc, func, or_
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

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
        "date_creation": aide.date_creation,
        "date_consultation": date_consultation,
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
    rows = (
        db.query(Aides, ConsultationAide.date_consultation)
        .join(ConsultationAide, ConsultationAide.aide_id == Aides.aide_id)
        .filter(ConsultationAide.user_id == user.user_id)
        .order_by(desc(ConsultationAide.date_consultation), desc(ConsultationAide.id))
        .limit(limit)
        .all()
    )
    return [_serialize_aid(aide, date_consultation=date_consultation) for aide, date_consultation in rows]


def _profile_match_filters(user: Utilisateur):
    filters = []
    ville = getattr(user, "ville", None) or user.region
    if ville:
        filters.append(
            or_(
                Aides.region_cible.is_(None),
                Aides.region_cible.ilike("%Maroc%"),
                Aides.region_cible.ilike(f"%{ville}%"),
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
                Aides.statut_socio_pro_requis.ilike("%Tous%"),
                Aides.statut_socio_pro_requis.ilike(f"%{user.statut_socio_pro}%"),
            )
        )
    return filters


def _recommendation_score(user: Utilisateur):
    ville = getattr(user, "ville", None) or user.region
    score_parts = []
    if ville:
        score_parts.append(
            case(
                (
                    or_(
                        Aides.region_cible.ilike(f"%{ville}%"),
                        Aides.region_cible.ilike("%Maroc%"),
                    ),
                    40,
                ),
                (Aides.region_cible.is_(None), 20),
                else_=0,
            )
        )
    if user.statut_socio_pro:
        score_parts.append(
            case(
                (Aides.statut_socio_pro_requis.ilike(f"%{user.statut_socio_pro}%"), 30),
                (
                    or_(
                        Aides.statut_socio_pro_requis.is_(None),
                        Aides.statut_socio_pro_requis.ilike("%Tous%"),
                    ),
                    15,
                ),
                else_=0,
            )
        )
    if user.niveau_etude:
        score_parts.append(
            case(
                (Aides.niveau_etude_requis.ilike(f"%{user.niveau_etude}%"), 30),
                (
                    or_(
                        Aides.niveau_etude_requis.is_(None),
                        Aides.niveau_etude_requis.ilike("%Tous%"),
                    ),
                    15,
                ),
                else_=0,
            )
        )
    if not score_parts:
        return case((Aides.aide_id.isnot(None), 0), else_=0)
    return sum(score_parts)


def _recommendation_query(db: Session, user: Utilisateur):
    score = _recommendation_score(user).label("score_matching")
    filters = _profile_match_filters(user)
    query = db.query(Aides, score)
    if filters:
        query = query.filter(and_(*filters))
    if user.situation_handicap is not None:
        query = query.filter(or_(Aides.handicap_requis.is_(False), Aides.handicap_requis == user.situation_handicap))
    return query.order_by(desc(score), desc(Aides.date_creation), desc(Aides.aide_id))


def get_user_recommendations(db: Session, user: Utilisateur, limit: int = 10) -> list[dict]:
    rows = _recommendation_query(db, user).limit(limit).all()
    if not rows and _profile_match_filters(user):
        rows = db.query(Aides, _recommendation_score(user).label("score_matching")).order_by(
            desc(Aides.date_creation), desc(Aides.aide_id)
        ).limit(limit).all()
    return [_serialize_aid(aide, int(score_matching or 0)) for aide, score_matching in rows]


def count_user_recommendations(db: Session, user: Utilisateur, limit: int = 10) -> int:
    subquery = _recommendation_query(db, user).limit(limit).subquery()
    return db.query(func.count()).select_from(subquery).scalar() or 0


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
