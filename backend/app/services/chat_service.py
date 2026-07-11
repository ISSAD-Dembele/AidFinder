from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.datetime_utils import as_utc, utc_now
from app.models.discussion import Discussion
from app.models.historique import Historique
from app.models.resultat_chat import ResultatChatbot
from app.models.utilisateurs import Utilisateur
from app.services.conversation_brain import ConversationBrain
from app.services.conversation_engine import ConversationMeta
from app.services.recommendation_engine import recommendation_engine
from app.services.response_generator import ResponseGenerator

MAX_HISTORY_MESSAGES = 10
MAX_RESPONSE_CHARS = 2500


def _clean_text(value: Any, limit: int | None = None) -> str:
    text = " ".join(str(value or "").split())
    if limit is not None and len(text) > limit:
        return f"{text[:limit].rstrip()}..."
    return text


def _calculate_age(date_naissance: date | None) -> int | None:
    if date_naissance is None:
        return None
    today = date.today()
    return today.year - date_naissance.year - (
        (today.month, today.day) < (date_naissance.month, date_naissance.day)
    )


class ConversationMemory:
    def get_or_create_history(
        self,
        db: Session,
        user: Utilisateur,
        message: str,
        historique_id: int | None = None,
    ) -> Historique:
        if historique_id:
            history_item = (
                db.query(Historique)
                .filter(
                    Historique.historique_id == historique_id,
                    Historique.user_id == user.user_id,
                )
                .first()
            )
            if not history_item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Discussion introuvable.",
                )
            return history_item

        title = _clean_text(message, 40)
        history_item = Historique(
            user_id=user.user_id,
            titre_resume=title or "Nouvelle discussion",
        )
        db.add(history_item)
        db.flush()
        return history_item

    def load_recent_messages(
        self,
        db: Session,
        history_item: Historique,
        limit: int = MAX_HISTORY_MESSAGES,
    ) -> list[dict]:
        messages = (
            db.query(Discussion)
            .filter(Discussion.historique_id == history_item.historique_id)
            .order_by(desc(Discussion.date_creation), desc(Discussion.discussion_id))
            .limit(limit)
            .all()
        )
        messages.reverse()
        return [
            {
                "role": message.expediteur,
                "content": _clean_text(message.contenu, 700),
            }
            for message in messages
        ]


def _build_user_profile(user: Utilisateur) -> dict:
    return {
        "ville": user.ville or "",
        "region": user.region or "",
        "niveau_etude": user.niveau_etude or "",
        "statut_socio_pro": user.statut_socio_pro or "",
        "age": _calculate_age(user.date_naissance),
        "handicap": user.situation_handicap if user.situation_handicap is not None else "",
    }


class ChatService:
    def __init__(self) -> None:
        self.memory = ConversationMemory()
        self.brain = ConversationBrain()
        self.generator = ResponseGenerator()

    def handle_message(
        self,
        db: Session,
        user: Utilisateur,
        message: str,
        historique_id: int | None = None,
    ) -> dict:
        clean_message = _clean_text(message)
        if not clean_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le message ne peut pas être vide.",
            )

        history_item = self.memory.get_or_create_history(
            db, user, clean_message, historique_id
        )
        meta = ConversationMeta.from_json(history_item.conversation_meta)
        db_profile = _build_user_profile(user)
        decision = self.brain.decide(clean_message, meta, db_profile)

        meta.previous_state = meta.state
        meta.state = decision.new_state
        meta.collected_fields.update(decision.extracted_info)

        recommendations = None
        if decision.should_recommend:
            recommendations = recommendation_engine.get_recommendations(
                db, decision.merged_profile, limit=5
            )
            meta.recommendation_shown = True
            meta.last_recommended_aids = [
                r["aide_id"] for r in (recommendations or [])
            ]

        try:
            bot_text = self.generator.generate(
                decision, meta, clean_message, recommendations
            )
            user_msg = Discussion(
                historique_id=history_item.historique_id,
                expediteur="user",
                contenu=clean_message,
            )
            bot_msg = Discussion(
                historique_id=history_item.historique_id,
                expediteur="assistant",
                contenu=bot_text,
            )
            db.add(user_msg)
            db.add(bot_msg)
            history_item.conversation_meta = meta.to_json()
            history_item.date_derniere_activite = utc_now()

            if recommendations:
                for r in recommendations:
                    db.add(
                        ResultatChatbot(
                            historique_id=history_item.historique_id,
                            aide_id=r["aide_id"],
                            score_matching=r["score_matching"],
                        )
                    )
            db.commit()
            db.refresh(history_item)
        except Exception:
            db.rollback()
            raise

        missing_fields = (
            self.brain.profile_collector.missing_fields(decision.merged_profile)
        )
        question = (
            self.brain.profile_collector.get_question(decision.field_to_ask)
            if decision.field_to_ask
            else None
        )
        suggestions = (
            self.brain.profile_collector.get_suggestions(decision.field_to_ask)
            if decision.field_to_ask
            else []
        )

        return {
            "historique_id": history_item.historique_id,
            "titre_resume": history_item.titre_resume,
            "date_derniere_activite": as_utc(history_item.date_derniere_activite),
            "user_message": {
                "discussion_id": user_msg.discussion_id,
                "expediteur": user_msg.expediteur,
                "contenu": user_msg.contenu,
                "date_creation": as_utc(user_msg.date_creation),
            },
            "bot_message": {
                "discussion_id": bot_msg.discussion_id,
                "expediteur": bot_msg.expediteur,
                "contenu": bot_msg.contenu,
                "date_creation": as_utc(bot_msg.date_creation),
            },
            "aides_recommandees": recommendations or [],
            "conversation_state": meta.state.value,
            "champs_manquants": missing_fields,
            "question_actuelle": question,
            "suggestions": suggestions,
        }


chat_service = ChatService()