import json
import re
from datetime import date
from typing import Any

from app.services.conversation_engine import (
    ConversationDecision,
    ConversationMeta,
    ConversationState,
    IntentCategory,
    StateMachine,
)
from app.services.llm_client import llm_client


class IntentDetector:
    PATTERNS: dict[IntentCategory, re.Pattern] = {
        IntentCategory.GREETING: re.compile(
            r"^(bonjour|salut|bonsoir|hello|coucou|hey|cc|salam|bsr|bonsoir)[\s!?.]*$",
            re.I,
        ),
        IntentCategory.HOW_ARE_YOU: re.compile(
            r"(comment\s*(?:vas|allez)\s*(?:tu|vous)?|comment\s*ça\s*va|ça\s*va\s*[?]?)",
            re.I,
        ),
        IntentCategory.SEARCH_JOB: re.compile(
            r"(emploi|travail|recrutement|job|carrière|chômage|pôle[-\s]emploi"
            r"|cherche\s*(?:un|du)\s*(?:emploi|travail)|offre\s*d['\']emploi)",
            re.I,
        ),
        IntentCategory.SEARCH_STUDY: re.compile(
            r"(étude|étudiant|bourse|formation|université|faculté|école"
            r"|diplôme|scolarité|stage|apprentissage|alternance)",
            re.I,
        ),
        IntentCategory.SEARCH_HOUSING: re.compile(
            r"(logement|appartement|maison|habitat|location|hébergement"
            r"|aide\s*au\s*logement|allocations?\s*logement)",
            re.I,
        ),
        IntentCategory.SEARCH_HEALTH: re.compile(
            r"(santé|médical|handicap|maladie|soin|mutuelle|assurance\s*maladie"
            r"|couverture\s*médicale|ramed|amostip)",
            re.I,
        ),
        IntentCategory.SEARCH_BUSINESS: re.compile(
            r"(entreprise|création|projet|financement|startup"
            r"|entrepreneur|business|indépendant|auto-entrepreneur)",
            re.I,
        ),
        IntentCategory.ASK_PROFILE: re.compile(
            r"(mon\s*profil|mes\s*informations|que\s*sais[-\s]tu"
            r"|quelles\s*infos|que\s*connais[-\s]tu)",
            re.I,
        ),
        IntentCategory.ASK_BEST: re.compile(
            r"(meilleur|mieux|top|priorité|le\s*plus\s*pertinent"
            r"|la\s*plus\s*pertinente|lequel|laquelle|recommander)",
            re.I,
        ),
        IntentCategory.ASK_DETAILS: re.compile(
            r"(détail|précision|plus\s*d['\"]infos?|explique"
            r"|comment\s*ça\s*marche|en\s*savoir\s*plus|développe)",
            re.I,
        ),
        IntentCategory.THANKS: re.compile(
            r"(merci|merci\s*beaucoup|merci\s*bien|je\s*te\s*remercie|merci\s*infiniement)",
            re.I,
        ),
        IntentCategory.GOODBYE: re.compile(
            r"(au\s*revoir|bye|à\s*plus|à\s*bientôt|ciao|adieu|bonne\s*journée)",
            re.I,
        ),
        IntentCategory.HELP: re.compile(
            r"(aide|que\s*fais[-\s]tu|comment\s*ça\s*marche"
            r"|à\s*quoi\s*ça\s*sert|comment\s*tu\s*fonctionnes)",
            re.I,
        ),
        IntentCategory.ASK_SPECIFIC_AID: re.compile(
            r"(aide\s+(?:appelée?|nommé|intitulé)|qu['\"]est-ce\s*que\s*"
            r"|c['\"]est\s*quoi|parle[-\s]moi\s*de)",
            re.I,
        ),
    }

    def detect(self, message: str, meta: ConversationMeta) -> IntentCategory:
        stripped = message.strip()

        # The LLM decides how to interpret the message — not the intent detector.
        # We only detect explicit intents for context tracking.
        for intent, pattern in self.PATTERNS.items():
            if pattern.search(stripped):
                return intent

        return IntentCategory.UNKNOWN


class ProfileCollector:
    REQUIRED_FIELDS = ["ville", "region", "niveau_etude", "statut_socio_pro", "age", "handicap"]

    EXTRACTION_PATTERNS: dict[str, re.Pattern] = {
        "ville": re.compile(
            r"(?:j['\"]habite\s*(?:à|dans?|sur|près\s*de)\s*)([\w\s\-']+?)(?:\.|,|\s*et|\s*je|$)",
            re.I,
        ),
        "region": re.compile(
            r"(?:région|region)\s*(?:de\s*)?([\w\s\-']+)", re.I
        ),
        "niveau_etude": re.compile(
            r"(sans\s*diplome|sans\s*diplôme|bac|baccalauréat|baccalaureat"
            r"|licence|master|doctorat|ingénieur|ingenieur"
            r"|bts|dut|cap|brevet|bac\+[0-9])",
            re.I,
        ),
        "statut_socio_pro": re.compile(
            r"(étudiant|etudiant|employé|employe|salarié|salarie"
            r"|demandeur\s*d['\"]?emploi|chômeur|chomeur"
            r"|indépendant|independant|retraité|retraite"
            r"|stagiaire|fonctionnaire|sans\s*emploi)",  # noqa: E501
            re.I,
        ),
        "age": re.compile(r"(?:j['\"]ai|âge|age)\s*(\d+)\s*(?:ans)", re.I),
        "handicap": re.compile(
            r"(?:handicap|situation\s*de\s*handicap|rqth|reconnaissance\s*handicap"
            r"|handicapé|handicapee|handicapée|aménagements?)",  # noqa: E501
            re.I,
        ),
    }

    QUESTIONS: dict[str, str] = {
        "ville": "Dans quelle ville habitez-vous ?",
        "region": "Dans quelle région se trouve votre ville ?",
        "niveau_etude": (
            "Quel est votre niveau d'étude ?\n\n"
            "Exemples : sans diplôme, bac, licence, master, doctorat"
        ),
        "statut_socio_pro": (
            "Quelle est votre situation actuelle ?\n\n"
            "Exemples : étudiant, employé, demandeur d'emploi, indépendant, retraité"
        ),
        "age": "Quel âge avez-vous ? (pour vérifier votre éligibilité aux aides)",
        "handicap": "Avez-vous une situation de handicap reconnue ?",
    }

    SUGGESTIONS: dict[str, list[str]] = {
        "ville": [
            "Casablanca",
            "Rabat",
            "Marrakech",
            "Fès",
            "Tanger",
            "Agadir",
            "Oujda",
            "Meknès",
        ],
        "region": [
            "Casablanca-Settat",
            "Rabat-Salé-Kénitra",
            "Marrakech-Safi",
            "Fès-Meknès",
            "Tanger-Tétouan-Al Hoceïma",
        ],
        "niveau_etude": [
            "Sans diplôme",
            "Bac",
            "Bac+2",
            "Licence",
            "Master",
            "Doctorat",
        ],
        "statut_socio_pro": [
            "Étudiant",
            "Employé",
            "Demandeur d'emploi",
            "Indépendant",
            "Retraité",
            "Stagiaire",
        ],
        "handicap": ["Oui", "Non"],
    }

    def extract(self, message: str) -> dict[str, Any]:
        extracted: dict[str, Any] = {}
        for field, pattern in self.EXTRACTION_PATTERNS.items():
            match = pattern.search(message)
            if not match:
                continue
            if field == "age":
                try:
                    extracted[field] = int(match.group(1))
                except (ValueError, IndexError):
                    pass
            elif field == "handicap":
                extracted[field] = True
            elif match.lastindex and match.group(1):
                extracted[field] = match.group(1).strip().capitalize()
            else:
                extracted[field] = match.group(0).strip().capitalize()
        return extracted

    def extract_with_llm(self, message: str) -> dict[str, Any]:
        if not llm_client.is_available:
            return {}
        prompt = (
            "Tu es un extracteur d'informations. Extrais les données suivantes "
            "du message utilisateur.\n"
            "Champs possibles : ville, region, niveau_etude, statut_socio_pro, age, handicap\n"
            "Retourne UNIQUEMENT un objet JSON valide avec les champs trouvés.\n"
            "Si un champ n'est pas trouvé, ne l'inclus pas dans le JSON.\n"
            "Ne mets JAMAIS de texte avant ou après le JSON.\n\n"
            f"Message : {message}\n\n"
            "JSON :"
        )
        result = llm_client.generate([{"role": "user", "content": prompt}])
        if not result:
            return {}
        try:
            cleaned = result.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.strip("`").strip()
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:].strip()
            return json.loads(cleaned)
        except (json.JSONDecodeError, TypeError):
            return {}

    def is_complete(self, profile: dict) -> bool:
        return all(
            profile.get(field) is not None and profile.get(field) != ""
            for field in self.REQUIRED_FIELDS
        )

    def missing_fields(self, profile: dict) -> list[str]:
        return [
            field
            for field in self.REQUIRED_FIELDS
            if profile.get(field) is None or profile.get(field) == ""
        ]

    def next_missing_field(self, profile: dict) -> str | None:
        for field in self.REQUIRED_FIELDS:
            value = profile.get(field)
            if value is None or value == "":
                return field
        return None

    def get_question(self, field: str) -> str:
        return self.QUESTIONS.get(field, f"Pouvez-vous me donner votre {field} ?")

    def get_suggestions(self, field: str) -> list[str]:
        return self.SUGGESTIONS.get(field, [])


class ConversationBrain:
    def __init__(self) -> None:
        self.intent_detector = IntentDetector()
        self.profile_collector = ProfileCollector()
        self.state_machine = StateMachine()

    def decide(
        self,
        user_message: str,
        conversation_meta: ConversationMeta,
        user_profile: dict,
    ) -> ConversationDecision:
        intent = self.intent_detector.detect(user_message, conversation_meta)
        extracted = self.profile_collector.extract(user_message)
        merged = self._merge_profiles(user_profile, conversation_meta.collected_fields, extracted)
        profile_complete = self.profile_collector.is_complete(merged)
        new_state = self.state_machine.next_state(
            conversation_meta.state, intent, profile_complete
        )
        should_recommend = self._should_recommend(
            intent, new_state, profile_complete, conversation_meta
        )

        return ConversationDecision(
            intent=intent,
            new_state=new_state,
            should_recommend=should_recommend,
            # The LLM decides whether to ask questions — not the state machine
            should_ask_question=False,
            field_to_ask=None,
            extracted_info=extracted,
            merged_profile=merged,
            # LLM also decides when clarification is needed
            clarification_needed=False,
        )

    def _should_recommend(
        self,
        intent: IntentCategory,
        new_state: ConversationState,
        profile_complete: bool,
        meta: ConversationMeta,
    ) -> bool:
        if new_state == ConversationState.RECOMMENDING:
            return True
        if meta.recommendation_shown:
            return False
        if profile_complete and intent in {
            IntentCategory.SEARCH_JOB,
            IntentCategory.SEARCH_STUDY,
            IntentCategory.SEARCH_HOUSING,
            IntentCategory.SEARCH_HEALTH,
            IntentCategory.SEARCH_BUSINESS,
            IntentCategory.ASK_BEST,
        }:
            return True
        return False

    def _merge_profiles(
        self, db_profile: dict, collected: dict, extracted: dict
    ) -> dict:
        merged = dict(db_profile)
        merged.update(collected)
        merged.update(extracted)
        return merged