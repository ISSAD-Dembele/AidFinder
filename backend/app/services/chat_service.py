"""
Chat service for AidFinder.

Handles the full message lifecycle:
1. Load/create history
2. Detect intent & decide state
3. Collect profile info
4. Compute recommendations (if needed)
5. Generate LLM response (with history context)
6. Save messages & recommendations
7. Return response with dynamic suggestions
"""

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
from app.services.conversation_engine import ConversationMeta, IntentCategory
from app.services.recommendation_engine import recommendation_engine
from app.services.response_generator import response_generator

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


def _compute_dynamic_suggestions(
    decision: Any,
    meta: ConversationMeta,
    user: Utilisateur,
    recommendations: list[dict] | None,
) -> list[str]:
    """
    Compute dynamic suggestions based on:
    - conversation state
    - profile completeness
    - existing recommendations
    - user intent
    """
    suggestions: list[str] = []

    # If we need to ask a profile field, suggest answers
    if decision.field_to_ask:
        from app.services.conversation_brain import ProfileCollector
        collector = ProfileCollector()
        return collector.get_suggestions(decision.field_to_ask)

    # If recommendations exist, let user interact with them
    if recommendations:
        suggestions.append("Donne-moi plus de détails")
        suggestions.append("Voir toutes les aides recommandées")
        suggestions.append("Je cherche autre chose")

    # General suggestions based on state
    state = meta.state
    if state.value == "GREETING" or decision.intent in (
        IntentCategory.GREETING, IntentCategory.HELP
    ):
        suggestions = [
            "Je cherche un emploi",
            "Je veux faire des études",
            "J'ai besoin d'un logement",
            "Aide pour la santé",
        ]
    elif state.value == "COLLECTING_INFO":
        if not decision.field_to_ask:
            suggestions = [
                "Je cherche un emploi",
                "Je veux faire des études",
            ]
    elif state.value == "DISCUSSING":
        suggestions = [
            "Je veux voir plus d'aides",
            "Explique-moi mieux",
            "Je cherche autre chose",
        ]

    # Deduplicate and limit
    seen = set()
    unique = []
    for s in suggestions:
        if s not in seen:
            seen.add(s)
            unique.append(s)
    return unique[:6]


class ChatService:
    def __init__(self) -> None:
        self.memory = ConversationMemory()
        self.brain = ConversationBrain()

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

        # Load conversation history for LLM context
        history = self.memory.load_recent_messages(db, history_item)

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
            bot_text = response_generator.generate(
                decision,
                meta,
                clean_message,
                history=history,
                recommendations=recommendations,
            )
            user_msg = Discussion(
                historique_id=history_item.historique_id,
                expediteur="user",
                contenu=clean_message,
            )
            bot_msg = Discussion(
                historique_id=history_item.historique_id,
                expediteur="assistant",
                contenu=_clean_text(bot_text, MAX_RESPONSE_CHARS),
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

        # Dynamic suggestions
        suggestions = _compute_dynamic_suggestions(
            decision, meta, user, recommendations
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
            "suggestions": suggestions,
        }

    async def handle_message_stream(
        self,
        db: Session,
        user: Utilisateur,
        message: str,
        historique_id: int | None = None,
    ):
        """
        Async generator for streaming responses.
        Yields chunks as they arrive from the LLM, then yields the final metadata.
        """
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

        history = self.memory.load_recent_messages(db, history_item)

        recommendations = None
        if decision.should_recommend:
            recommendations = recommendation_engine.get_recommendations(
                db, decision.merged_profile, limit=5
            )
            meta.recommendation_shown = True
            meta.last_recommended_aids = [
                r["aide_id"] for r in (recommendations or [])
            ]

        # Save user message immediately
        user_msg = Discussion(
            historique_id=history_item.historique_id,
            expediteur="user",
            contenu=clean_message,
        )
        db.add(user_msg)

        # Prepare bot message placeholder
        bot_msg = Discussion(
            historique_id=history_item.historique_id,
            expediteur="assistant",
            contenu="",
        )
        db.add(bot_msg)
        db.flush()

        try:
            full_text_parts: list[str] = []
            async for chunk in response_generator.generate_stream(
                decision,
                meta,
                clean_message,
                history=history,
                recommendations=recommendations,
            ):
                full_text_parts.append(chunk)
                yield {"type": "chunk", "data": chunk}

            full_text = "".join(full_text_parts)

            # Save message & recommendations
            bot_msg.contenu = _clean_text(full_text, MAX_RESPONSE_CHARS)
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

            # Build metadata
            missing_fields = (
                self.brain.profile_collector.missing_fields(decision.merged_profile)
            )
            suggestions = _compute_dynamic_suggestions(
                decision, meta, user, recommendations
            )

            yield {
                "type": "done",
                "data": {
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
                    "suggestions": suggestions,
                },
            }

        except Exception:
            db.rollback()
            raise


chat_service = ChatService()