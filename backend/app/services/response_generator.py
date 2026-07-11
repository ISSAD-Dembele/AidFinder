"""
Response generator for AidFinder.

LLM-first approach: tries OpenRouter → Qwen → conversation engine fallback.
The LLM produces ALL responses naturally - no more hardcoded if/else replies.
"""

from __future__ import annotations

import json
from typing import Any

from app.services.conversation_engine import (
    ConversationDecision,
    ConversationMeta,
    ConversationState,
    IntentCategory,
)
from app.services.llm_client import llm_client


# ─── Prompt builder ─────────────────────────────────────────────────────

class PromptBuilder:
    """Builds the full context prompt for the LLM."""

    HISTORY_TEMPLATE = (
        "Voici l'historique de la conversation :\n{history}\n"
    )
    RECOMMENDATIONS_TEMPLATE = (
        "\nVoici les aides disponibles recommandées (JSON) :\n{aids}\n"
    )

    SYSTEM_PROMPT = (
        "Tu es AidFinder, un assistant conversationnel spécialisé "
        "dans l'orientation vers les aides financières et sociales au Maroc.\n\n"
        "RÈGLES STRICTES :\n"
        "1. Tu réponds TOUJOURS de manière naturelle et chaleureuse, comme un vrai conseiller.\n"
        "2. Tu n'inventes JAMAIS une aide qui n'est pas dans la liste fournie.\n"
        "3. Si l'utilisateur demande des informations que tu n'as pas, dis-le honnêtement.\n"
        "4. Tu poses UNE SEULE question à la fois.\n"
        "5. Utilise les émojis avec parcimonie (👋 😊 👍).\n"
        "6. Ne liste toutes les aides que si l'utilisateur le demande explicitement.\n"
        "7. Si l'utilisateur donne une information, remercie-le et passe à l'étape suivante.\n"
        "8. Si l'utilisateur te salue (bonjour, salut, etc.), réponds de manière naturelle "
        "et demande-lui ce qu'il cherche.\n"
        "9. Si l'utilisateur te dit merci, réponds avec bienveillance.\n"
        "10. Si l'utilisateur dit au revoir, réponds chaleureusement et termine la conversation.\n"
        "11. Si l'utilisateur demande comment tu vas, réponds de manière naturelle.\n"
        "12. Tu es AidFinder, pas un assistant générique.\n\n"
    )

    def build_system_prompt(
        self,
        decision: ConversationDecision,
        meta: ConversationMeta,
        history: list[dict] | None = None,
        recommendations: list[dict] | None = None,
    ) -> str:
        profile_str = json.dumps(decision.merged_profile, default=str, ensure_ascii=False)

        parts = [self.SYSTEM_PROMPT]

        # User profile
        parts.append(f"Profil utilisateur : {profile_str}\n")

        # Conversation state
        parts.append(f"État conversationnel : {decision.new_state.value}\n")
        parts.append(f"Intention détectée : {decision.intent.value}\n")

        # History
        if history:
            history_str = "\n".join(
                f"{'Utilisateur' if m['role'] == 'user' else 'AidFinder'} : "
                f"{m['content']}"
                for m in history[-10:]
            )
            parts.append(self.HISTORY_TEMPLATE.format(history=history_str))

        # Recommended aids if available
        if recommendations:
            aids_json = json.dumps(
                [
                    {
                        "titre": r["titre"],
                        "description": r.get("description", ""),
                        "categorie": r.get("categorie", ""),
                        "score_matching": r.get("score_matching", 0),
                        "raisons": r.get("raisons", []),
                        "region_cible": r.get("region_cible"),
                        "niveau_etude_requis": r.get("niveau_etude_requis"),
                        "statut_socio_pro_requis": r.get("statut_socio_pro_requis"),
                        "age_min": r.get("age_min"),
                        "age_max": r.get("age_max"),
                        "handicap_requis": r.get("handicap_requis"),
                        "lien_officiel": r.get("lien_officiel"),
                    }
                    for r in recommendations
                ],
                default=str,
                ensure_ascii=False,
            )
            parts.append(self.RECOMMENDATIONS_TEMPLATE.format(aids=aids_json))
            parts.append(
                "RAPPEL : Tu ne dois JAMAIS inventer une aide. "
                "Tu ne peux parler que des aides listées ci-dessus.\n"
            )

        # Missing fields / question to ask
        if decision.field_to_ask:
            parts.append(
                f"Tu dois demander à l'utilisateur : "
                f"'{decision.field_to_ask}' (formule une question naturelle)\n"
            )

        parts.append(
            "Réponds maintenant au message de l'utilisateur de manière naturelle, "
            "chaleureuse et concise."
        )

        return "\n".join(parts)

    def build_messages(
        self,
        decision: ConversationDecision,
        meta: ConversationMeta,
        user_message: str,
        history: list[dict] | None = None,
        recommendations: list[dict] | None = None,
    ) -> list[dict]:
        system = self.build_system_prompt(decision, meta, history, recommendations)
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ]


# ─── Fallback: conversation engine (LLM unavailable) ───────────────────

class ConversationFallback:
    """
    Fallback engine that uses the existing conversation state machine
    to produce responses when the LLM is unavailable.
    No hardcoded templates - uses the brain's decision to construct responses.
    """

    def generate(
        self,
        decision: ConversationDecision,
        meta: ConversationMeta,
        history: list[dict] | None = None,
        recommendations: list[dict] | None = None,
    ) -> str:
        state = decision.new_state
        intent = decision.intent

        # ── Greeting / social conversation ──────────────────────────
        if intent in (IntentCategory.GREETING, IntentCategory.HOW_ARE_YOU, IntentCategory.HELP):
            return self._greeting_response(state, intent, decision)

        if intent == IntentCategory.THANKS:
            return self._thanks_response()

        if intent == IntentCategory.GOODBYE:
            return self._goodbye_response()

        # ── Profile query ───────────────────────────────────────────
        if intent == IntentCategory.ASK_PROFILE:
            return self._profile_response(decision.merged_profile)

        # ── Recommendations ─────────────────────────────────────────
        if decision.should_recommend and recommendations:
            return self._recommendation_response(recommendations)

        if decision.should_recommend and not recommendations:
            return (
                "Je n'ai malheureusement trouvé aucune aide correspondant "
                "à votre profil dans notre base actuelle. 😕\n\n"
                "Je vous invite à revenir plus tard, de nouvelles aides "
                "sont ajoutées régulièrement."
            )

        # ── Collecting info / asking question ───────────────────────
        if decision.field_to_ask:
            from app.services.conversation_brain import ProfileCollector
            collector = ProfileCollector()
            return collector.get_question(decision.field_to_ask)

        # ── Clarification ───────────────────────────────────────────
        if decision.clarification_needed:
            return (
                "Je n'ai pas bien compris votre demande. 🤔\n\n"
                "Pouvez-vous reformuler ? Par exemple :\n"
                "• \"Je cherche un emploi\"\n"
                "• \"Je veux poursuivre mes études\"\n"
                "• \"J'ai besoin d'un logement\""
            )

        # ── Default ─────────────────────────────────────────────────
        return (
            "Je suis là pour vous aider à trouver des aides "
            "financières et sociales adaptées à votre situation.\n\n"
            "Que recherchez-vous comme aide ?"
        )

    def _greeting_response(self, state: ConversationState, intent: IntentCategory,
                           decision: ConversationDecision) -> str:
        if intent == IntentCategory.HOW_ARE_YOU:
            return (
                "Je vais très bien, merci ! 😊\n\n"
                "Je suis AidFinder, votre assistant pour trouver "
                "des aides financières et sociales au Maroc.\n\n"
                "Que puis-je faire pour vous aujourd'hui ?"
            )
        if intent == IntentCategory.HELP:
            return (
                "Je suis AidFinder, votre assistant pour trouver des aides "
                "financières et sociales au Maroc. 🤖\n\n"
                "Je peux vous aider à :\n"
                "• Trouver des aides pour l'emploi, les études, le logement, la santé\n"
                "• Vérifier votre éligibilité aux différentes aides\n"
                "• Vous orienter vers les bons organismes\n\n"
                "Dites-moi ce que vous cherchez !"
            )
        return (
            "Bonjour 👋\n\n"
            "Je suis AidFinder. Je suis là pour vous accompagner "
            "dans la recherche des aides financières auxquelles "
            "vous pourriez être éligible.\n\n"
            "Comment puis-je vous aider aujourd'hui ?"
        )

    def _thanks_response(self) -> str:
        return (
            "Avec plaisir ! 😊\n\n"
            "N'hésitez pas si vous avez d'autres questions, "
            "je suis là pour vous aider."
        )

    def _goodbye_response(self) -> str:
        return (
            "Au revoir et bonne journée ! 😊\n\n"
            "N'hésitez pas à revenir sur AidFinder "
            "si vous avez besoin d'aide. À bientôt !"
        )

    def _profile_response(self, profile: dict) -> str:
        filled = {k: v for k, v in profile.items() if v}
        missing = [
            f for f in ["ville", "region", "niveau_etude",
                        "statut_socio_pro", "age", "handicap"]
            if not profile.get(f)
        ]
        msg = "Voici ce que je sais de vous :\n\n"
        labels = {
            "ville": "Ville", "region": "Région",
            "niveau_etude": "Niveau d'étude",
            "statut_socio_pro": "Situation",
            "age": "Âge", "handicap": "Handicap",
        }
        for k, v in filled.items():
            msg += f"• {labels.get(k, k)} : {v}\n"
        if missing:
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


# ─── Main ResponseGenerator ────────────────────────────────────────────

class ResponseGenerator:
    """
    LLM-first response generator.
    Tries: OpenRouter → Qwen → ConversationFallback
    """

    def __init__(self) -> None:
        self.prompt_builder = PromptBuilder()
        self.fallback = ConversationFallback()

    def generate(
        self,
        decision: ConversationDecision,
        meta: ConversationMeta,
        user_message: str,
        history: list[dict] | None = None,
        recommendations: list[dict] | None = None,
    ) -> str:
        # Always try LLM first
        if llm_client.is_available:
            messages = self.prompt_builder.build_messages(
                decision, meta, user_message, history, recommendations
            )
            response = llm_client.generate(messages)
            if response and response.strip():
                return response

        # Fallback to conversation engine
        return self.fallback.generate(decision, meta, history, recommendations)

    async def generate_stream(
        self,
        decision: ConversationDecision,
        meta: ConversationMeta,
        user_message: str,
        history: list[dict] | None = None,
        recommendations: list[dict] | None = None,
    ):
        """Async generator yielding response text chunks."""
        if not llm_client.is_available:
            # No LLM → yield the fallback as a single chunk
            text = self.fallback.generate(decision, meta, history, recommendations)
            yield text
            return

        messages = self.prompt_builder.build_messages(
            decision, meta, user_message, history, recommendations
        )
        stream = await llm_client.generate_stream(messages)

        if stream is None:
            # Stream not available → fallback
            text = self.fallback.generate(decision, meta, history, recommendations)
            yield text
            return

        async with stream:
            async for chunk in stream.iter_text_chunks():
                yield chunk


# Singleton
response_generator = ResponseGenerator()