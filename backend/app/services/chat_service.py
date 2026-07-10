from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import requests
from fastapi import HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from app.core.config import (
    QWEN_API_KEY,
    QWEN_API_URL,
    QWEN_MAX_TOKENS,
    QWEN_MODEL,
    QWEN_TEMPERATURE,
    QWEN_TIMEOUT_SECONDS,
)
from app.core.datetime_utils import as_utc, utc_now
from app.models.aides import Aides
from app.models.discussion import Discussion
from app.models.historique import Historique
from app.models.resultat_chat import ResultatChatbot
from app.models.utilisateurs import Utilisateur
from app.services.dashboard_service import get_user_recommendations

MAX_CONTEXT_AIDS = 8
MAX_HISTORY_MESSAGES = 10
MAX_DESCRIPTION_CHARS = 420
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


@dataclass
class ChatContext:
    profile: dict
    history: list[dict]
    aids: list[dict]


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


class PromptBuilder:
    def build_context(
        self,
        db: Session,
        user: Utilisateur,
        history: list[dict],
    ) -> ChatContext:
        recommended = get_user_recommendations(db, user, limit=MAX_CONTEXT_AIDS)
        aids = self._load_aid_context(db, recommended)
        return ChatContext(
            profile=self._build_profile(user),
            history=history,
            aids=aids,
        )

    def build_messages(self, context: ChatContext, user_message: str) -> list[dict]:
        return [
            {
                "role": "system",
                "content": (
                    "Tu es l'assistant AidFinder. Reponds en francais, avec concision. "
                    "Tu dois utiliser uniquement les aides fournies dans le contexte. "
                    "N'invente jamais une aide, une condition, un montant, une source ou un lien. "
                    "Si le contexte ne contient pas l'information demandee, dis-le clairement et propose "
                    "de completer le profil ou de consulter le lien officiel quand il existe. "
                    "Quand l'utilisateur pose une question elliptique comme 'la meilleure ?', utilise "
                    "l'historique pour comprendre la reference."
                ),
            },
            {
                "role": "user",
                "content": self._render_context(context, user_message),
            },
        ]

    def _build_profile(self, user: Utilisateur) -> dict:
        return {
            "ville": user.ville or "non renseignee",
            "region": user.region or "non renseignee",
            "niveau_etude": user.niveau_etude or "non renseigne",
            "statut_socio_professionnel": user.statut_socio_pro or "non renseigne",
            "age": _calculate_age(user.date_naissance),
            "handicap": "oui" if user.situation_handicap else "non",
        }

    def _load_aid_context(self, db: Session, recommended: list[dict]) -> list[dict]:
        if not recommended:
            return []

        score_by_id = {item["aide_id"]: item for item in recommended}
        aids_by_id = {
            aide.aide_id: aide
            for aide in (
                db.query(Aides)
                .options(joinedload(Aides.categorie), joinedload(Aides.source))
                .filter(Aides.aide_id.in_(score_by_id.keys()))
                .all()
            )
        }

        aids = []
        for item in recommended:
            aide = aids_by_id.get(item["aide_id"])
            if aide is None:
                continue
            source_name = aide.source.nom if aide.source else None
            source_url = aide.source.url if aide.source else None
            aids.append(
                {
                    "aide_id": aide.aide_id,
                    "titre": _clean_text(aide.titre, 120),
                    "description": _clean_text(aide.description, MAX_DESCRIPTION_CHARS),
                    "categorie": aide.categorie.nom if aide.categorie else aide.type_aide,
                    "source": source_name,
                    "source_url": source_url,
                    "lien_officiel": aide.url_officielle or source_url,
                    "region_cible": aide.region_cible,
                    "niveau_etude_requis": aide.niveau_etude_requis,
                    "statut_socio_pro_requis": aide.statut_socio_pro_requis,
                    "age_min": aide.age_min,
                    "age_max": aide.age_max,
                    "handicap_requis": aide.handicap_requis,
                    "score_matching": item.get("score_matching"),
                    "raisons": item.get("raisons", [])[:5],
                }
            )
        return aids

    def _render_context(self, context: ChatContext, user_message: str) -> str:
        lines = [
            "CONTEXTE UTILISATEUR",
            f"- Ville: {context.profile['ville']}",
            f"- Region: {context.profile['region']}",
            f"- Niveau d'etude: {context.profile['niveau_etude']}",
            f"- Statut socio-professionnel: {context.profile['statut_socio_professionnel']}",
            f"- Age: {context.profile['age'] if context.profile['age'] is not None else 'non renseigne'}",
            f"- Situation de handicap: {context.profile['handicap']}",
            "",
            "HISTORIQUE RECENT",
        ]

        if context.history:
            lines.extend(
                f"- {message['role']}: {message['content']}"
                for message in context.history
            )
        else:
            lines.append("- Aucun message precedent.")

        lines.extend(["", "AIDES RECOMMANDEES DISPONIBLES"])
        if context.aids:
            for index, aide in enumerate(context.aids, start=1):
                lines.extend(
                    [
                        f"{index}. {aide['titre']} (id {aide['aide_id']}, score {aide['score_matching']}/100)",
                        f"   Description: {aide['description'] or 'non renseignee'}",
                        f"   Categorie: {aide['categorie'] or 'non renseignee'}",
                        f"   Source: {aide['source'] or 'non renseignee'}",
                        f"   Lien officiel: {aide['lien_officiel'] or 'non renseigne'}",
                        f"   Conditions: region={aide['region_cible'] or 'non restrictive'}; "
                        f"niveau={aide['niveau_etude_requis'] or 'non restrictif'}; "
                        f"statut={aide['statut_socio_pro_requis'] or 'non restrictif'}; "
                        f"age_min={aide['age_min']}; age_max={aide['age_max']}; "
                        f"handicap_requis={aide['handicap_requis']}",
                        f"   Raisons: {', '.join(aide['raisons']) if aide['raisons'] else 'non renseignees'}",
                    ]
                )
        else:
            lines.append("- Aucune aide compatible n'a ete trouvee dans la base.")

        lines.extend(
            [
                "",
                "CONSIGNES DE REPONSE",
                "- Reponds uniquement a partir des aides listees ci-dessus.",
                "- Cite les titres exacts et les liens officiels disponibles.",
                "- Pour 'la meilleure', considere le score de matching le plus eleve et les derniers messages.",
                "- Limite la reponse a 6 phrases ou une courte liste.",
                "",
                f"QUESTION UTILISATEUR: {_clean_text(user_message, 1000)}",
            ]
        )
        return "\n".join(lines)


class QwenClient:
    def generate(self, messages: list[dict]) -> str | None:
        if not QWEN_API_KEY:
            return None

        response = requests.post(
            QWEN_API_URL,
            headers={
                "Authorization": f"Bearer {QWEN_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": QWEN_MODEL,
                "messages": messages,
                "temperature": QWEN_TEMPERATURE,
                "max_tokens": QWEN_MAX_TOKENS,
            },
            timeout=QWEN_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
        choices = payload.get("choices") or []
        if not choices:
            return None
        content = choices[0].get("message", {}).get("content")
        return _clean_text(content, MAX_RESPONSE_CHARS) if content else None


class ChatService:
    def __init__(self) -> None:
        self.memory = ConversationMemory()
        self.prompt_builder = PromptBuilder()
        self.qwen_client = QwenClient()

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

        history_item = self.memory.get_or_create_history(db, user, clean_message, historique_id)
        previous_messages = self.memory.load_recent_messages(db, history_item)
        context = self.prompt_builder.build_context(db, user, previous_messages)
        qwen_messages = self.prompt_builder.build_messages(context, clean_message)

        try:
            bot_text = self.qwen_client.generate(qwen_messages) or self._fallback_answer(context)
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
            self._record_recommendation_results(db, history_item, context.aids)
            history_item.date_derniere_activite = utc_now()
            db.commit()
            db.refresh(user_msg)
            db.refresh(bot_msg)
            db.refresh(history_item)
        except requests.RequestException as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Le modèle Qwen est temporairement indisponible: {exc}",
            ) from exc
        except Exception:
            db.rollback()
            raise

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
            "aides_recommandees": [
                self._response_aid(aide) for aide in context.aids
            ],
        }

    def _record_recommendation_results(
        self,
        db: Session,
        history_item: Historique,
        aids: list[dict],
    ) -> None:
        for aide in aids:
            db.add(
                ResultatChatbot(
                    historique_id=history_item.historique_id,
                    aide_id=aide["aide_id"],
                    score_matching=aide.get("score_matching"),
                )
            )

    def _fallback_answer(self, context: ChatContext) -> str:
        if not context.aids:
            return (
                "Je n'ai trouvé aucune aide compatible dans les données disponibles. "
                "Je peux quand même vous orienter si vous complétez votre ville, région, âge, "
                "niveau d'étude, statut socio-professionnel et situation de handicap."
            )

        best = context.aids[0]
        link = f" Lien officiel: {best['lien_officiel']}." if best.get("lien_officiel") else ""
        reasons = ", ".join(best.get("raisons") or [])
        return (
            f"D'après votre profil, l'aide la plus pertinente est {best['titre']} "
            f"avec un score de compatibilité de {best['score_matching']}/100. "
            f"Elle ressort notamment pour ces raisons: {reasons or 'compatibilité avec le profil renseigné'}. "
            f"Je me base uniquement sur les aides présentes dans AidFinder.{link}"
        )

    def _response_aid(self, aide: dict) -> dict:
        return {
            "id": aide["aide_id"],
            "aide_id": aide["aide_id"],
            "titre": aide["titre"],
            "description": aide["description"],
            "image": None,
            "image_url": None,
            "categorie": aide["categorie"],
            "url_officielle": aide["lien_officiel"],
            "region_cible": aide["region_cible"],
            "type_aide": aide["categorie"],
            "score_matching": aide["score_matching"],
            "compatibilite": aide["score_matching"],
            "raisons": aide["raisons"],
            "date_creation": None,
            "date_consultation": None,
        }


chat_service = ChatService()
