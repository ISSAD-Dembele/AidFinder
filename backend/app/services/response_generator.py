import json
import random
from typing import Any

import requests

from app.core.config import (
    QWEN_API_KEY,
    QWEN_API_URL,
    QWEN_MAX_TOKENS,
    QWEN_MODEL,
    QWEN_TEMPERATURE,
    QWEN_TIMEOUT_SECONDS,
)
from app.services.conversation_engine import (
    ConversationDecision,
    ConversationMeta,
    ConversationState,
    IntentCategory,
)


class QwenClient:
    def __init__(self) -> None:
        self.is_available = bool(QWEN_API_KEY)

    def generate(self, messages: list[dict]) -> str | None:
        if not self.is_available:
            return None
        try:
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
            return self._clean(content) if content else None
        except requests.RequestException:
            return None

    def _clean(self, text: str) -> str:
        return " ".join(str(text or "").split())


class PromptBuilder:
    def build_system_prompt(
        self,
        decision: ConversationDecision,
        meta: ConversationMeta,
    ) -> str:
        profile_str = json.dumps(decision.merged_profile, default=str, ensure_ascii=False)
        return (
            "Tu es AidFinder, un assistant conversationnel français spécialisé "
            "dans l'orientation vers les aides financières et sociales au Maroc.\n\n"
            "RÈGLES STRICTES :\n"
            "1. Ne réponds JAMAIS par une simple liste d'aides.\n"
            "2. Sois naturel, chaleureux, comme un vrai conseiller.\n"
            "3. Si l'utilisateur te salue, salue-le en retour et demande-lui "
            "ce qu'il cherche.\n"
            "4. Pose UNE SEULE question à la fois.\n"
            "5. Ne modifie JAMAIS les informations des aides (score, lien, montant).\n"
            "6. Utilise les émojis avec parcimonie.\n"
            "7. Si l'utilisateur te donne une information, remercie-le.\n"
            "8. Ne liste toutes les aides que si l'utilisateur le demande "
            "explicitement.\n\n"
            f"État actuel : {decision.new_state.value}\n"
            f"Profil utilisateur : {profile_str}"
        )

    def build_prompt(
        self,
        decision: ConversationDecision,
        meta: ConversationMeta,
        user_message: str,
        recommendations: list[dict] | None = None,
    ) -> list[dict]:
        system = self.build_system_prompt(decision, meta)
        if recommendations:
            aids_json = json.dumps(recommendations, default=str, ensure_ascii=False)
            system += f"\n\nAides disponibles :\n{aids_json}"
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ]


class FallbackTemplates:
    def __init__(self) -> None:
        self._greeted = False

    def generate(
        self,
        decision: ConversationDecision,
        meta: ConversationMeta,
        recommendations: list[dict] | None = None,
    ) -> str:
        state = decision.new_state
        intent = decision.intent

        if state == ConversationState.GREETING or intent == IntentCategory.GREETING:
            self._greeted = True
            return random.choice([
                "Bonjour 👋\n\nJe suis AidFinder.\n"
                "Je suis là pour vous aider à trouver les aides financières "
                "auxquelles vous pouvez prétendre.\n\n"
                "Comment puis-je vous aider aujourd'hui ?",
                "Salut 😊\n\nBienvenue sur AidFinder.\n"
                "Que recherchez-vous aujourd'hui ?",
                "Bonjour !\n\nJe suis votre assistant AidFinder.\n"
                "Comment puis-je vous accompagner dans vos recherches ?",
            ])

        if intent == IntentCategory.HOW_ARE_YOU:
            return random.choice([
                "Je vais très bien merci 😊\nEt vous ?\n\n"
                "Que puis-je faire pour vous aujourd'hui ?",
                "Très bien, merci de demander ! 😊\n"
                "Comment puis-je vous aider ?",
            ])

        if intent == IntentCategory.THANKS:
            return random.choice([
                "Avec plaisir ! 😊\n"
                "N'hésitez pas si vous avez d'autres questions.",
                "Je vous en prie ! 😊\n"
                "Y a-t-il autre chose que je puisse faire pour vous ?",
            ])

        if intent == IntentCategory.GOODBYE:
            return random.choice([
                "Au revoir ! 😊\nBonne journée et à bientôt sur AidFinder.",
                "À bientôt ! 😊\n"
                "N'hésitez pas à revenir si vous avez besoin d'aide.",
            ])

        if intent == IntentCategory.HELP:
            return (
                "Je suis AidFinder, votre assistant pour trouver des aides "
                "financières et sociales au Maroc. 🤖\n\n"
                "Je peux vous aider à :\n"
                "• Trouver des aides pour l'emploi, les études, le logement, "
                "la santé\n"
                "• Vérifier votre éligibilité aux différentes aides\n"
                "• Vous orienter vers les bons organismes\n\n"
                "Dites-moi ce que vous cherchez !"
            )

        if intent == IntentCategory.ASK_PROFILE:
            return self._profile_response(decision.merged_profile)

        if decision.clarification_needed:
            return (
                "Je n'ai pas bien compris votre demande. 🤔\n\n"
                "Pouvez-vous reformuler ? Par exemple :\n"
                "• \"Je cherche un emploi\"\n"
                "• \"Je veux poursuivre mes études\"\n"
                "• \"J'ai besoin d'un logement\""
            )

        if decision.should_recommend and recommendations:
            return self._recommendation_response(recommendations)

        if decision.should_recommend and not recommendations:
            return (
                "Je n'ai malheureusement trouvé aucune aide correspondant "
                "à votre profil dans notre base actuelle. 😕\n\n"
                "Je vous invite à revenir plus tard, de nouvelles aides "
                "sont ajoutées régulièrement."
            )

        return (
            "Je suis là pour vous aider. "
            "Que recherchez-vous comme aide aujourd'hui ?"
        )

    def _profile_response(self, profile: dict) -> str:
        filled = {k: v for k, v in profile.items() if v}
        missing = [f for f in ["ville", "region", "niveau_etude",
                                "statut_socio_pro", "age", "handicap"]
                   if not profile.get(f)]
        msg = "Voici ce que je sais de vous :\n\n"
        for k, v in filled.items():
            labels = {
                "ville": "Ville", "region": "Région",
                "niveau_etude": "Niveau d'étude",
                "statut_socio_pro": "Situation",
                "age": "Âge", "handicap": "Handicap",
            }
            msg += f"• {labels.get(k, k)} : {v}\n"
        if missing:
            labels = {
                "ville": "votre ville", "region": "votre région",
                "niveau_etude": "votre niveau d'étude",
                "statut_socio_pro": "votre situation",
                "age": "votre âge", "handicap": "votre situation de handicap",
            }
            missing_labels = [labels.get(f, f) for f in missing]
            msg += (
                f"\nIl me manque : {', '.join(missing_labels)}.\n"
                "Puis-je vous poser quelques questions pour mieux vous aider ?"
            )
        return msg

    def _recommendation_response(self, recommendations: list[dict]) -> str:
        best = recommendations[0]
        raisons = ", ".join(best.get("raisons", []))
        lien = best.get("lien_officiel") or ""
        return (
            f"Parfait ! D'après votre profil, voici l'aide la plus adaptée "
            f"pour vous :\n\n"
            f"🏆 **{best['titre']}**\n"
            f"Score de compatibilité : {best['score_matching']}/100\n"
            f"Raisons : {raisons}\n"
            f"🔗 Lien officiel : {lien}\n\n"
            f"Souhaitez-vous plus de détails sur cette aide, "
            f"ou voir toutes les aides disponibles ?"
        )


class ResponseGenerator:
    def __init__(self) -> None:
        self.qwen = QwenClient()
        self.prompt_builder = PromptBuilder()
        self.fallback = FallbackTemplates()

    def generate(
        self,
        decision: ConversationDecision,
        meta: ConversationMeta,
        user_message: str,
        recommendations: list[dict] | None = None,
    ) -> str:
        if self.qwen.is_available:
            messages = self.prompt_builder.build_prompt(
                decision, meta, user_message, recommendations
            )
            response = self.qwen.generate(messages)
            if response:
                return response
        return self.fallback.generate(decision, meta, recommendations)