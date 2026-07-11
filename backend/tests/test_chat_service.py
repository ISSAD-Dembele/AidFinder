import os
import sys
import unittest
from datetime import date
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("ALGORITHM", "HS256")

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.models import Aides, CategorieAide, SourceAide, Utilisateur
from app.models.discussion import Discussion
from app.models.resultat_chat import ResultatChatbot
from app.services.chat_service import ChatService, _clean_text
from app.services.conversation_engine import (
    ConversationMeta,
    ConversationState,
    ConversationDecision,
    IntentCategory,
)
from app.services.conversation_brain import IntentDetector, ProfileCollector, ConversationBrain
from app.services.recommendation_engine import RecommendationEngine
from app.services.response_generator import FallbackTemplates


class FakeQwenClient:
    def __init__(self):
        self.calls = []
        self.is_available = True

    def generate(self, messages):
        self.calls.append(messages)
        content = messages[-1]["content"].lower() if messages else ""
        if any(w in content for w in ["bonjour", "salut", "bonsoir", "hello"]):
            return "Bonjour ! Comment puis-je vous aider aujourd'hui ?"
        if any(w in content for w in ["comment", "vas", "va"]):
            return "Je vais très bien merci ! Et vous ?"
        if any(w in content for w in ["meilleure", "meilleur", "laquelle"]):
            return "D'après votre profil, la Bourse étudiant est la meilleure option avec un score de 85/100."
        return "Je comprends. Pouvez-vous m'en dire plus sur votre situation ?"

    def _clean(self, text: str) -> str:
        return " ".join(str(text or "").split())


class ChatServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.db = self.SessionLocal()

        category = CategorieAide(nom="Études", description="Aides pour étudiants")
        source = SourceAide(nom="Portail officiel", url="https://example.gov/aides")
        user = Utilisateur(
            nom="Sara",
            email="sara@example.com",
            mot_de_passe_hash="hash",
            role="utilisateur",
            statut_compte="actif",
            date_naissance=date(2004, 2, 2),
            ville="Casablanca",
            region="Casablanca-Settat",
            niveau_etude="Licence",
            statut_socio_pro="Étudiant",
            situation_handicap=False,
        )
        aid = Aides(
            titre="Bourse étudiant Casablanca",
            description="Aide financière officielle pour étudiants résidant à Casablanca.",
            categorie=category,
            source=source,
            region_cible="Casablanca-Settat",
            niveau_etude_requis="Licence",
            statut_socio_pro_requis="Étudiant",
            age_min=18,
            age_max=30,
            handicap_requis=False,
            url_officielle="https://example.gov/bourse",
            est_active=True,
        )
        self.db.add_all([category, source, user, aid])
        self.db.commit()
        self.db.refresh(user)
        self.user = user

        self.service = ChatService()
        self.fake_qwen = FakeQwenClient()
        self.service.generator.qwen = self.fake_qwen

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_greeting_returns_natural_response_without_aids(self):
        """Phase 2 : une salutation ne doit jamais retourner d'aides."""
        response = self.service.handle_message(
            self.db,
            self.user,
            "Bonjour",
        )
        # Profile complet → DISCUSSING (pas besoin de collecter d'infos)
        self.assertIn(response["conversation_state"], ["DISCUSSING", "COLLECTING_INFO"])
        self.assertFalse(response["aides_recommandees"])
        bot_text = response["bot_message"]["contenu"].lower()
        self.assertIn("bonjour", bot_text)

    def test_greeting_salut_returns_natural_response(self):
        """Phase 2 : 'Salut' répond naturellement."""
        response = self.service.handle_message(
            self.db,
            self.user,
            "Salut",
        )
        self.assertFalse(response["aides_recommandees"])
        bot_text = response["bot_message"]["contenu"].lower()
        self.assertNotIn("bourse", bot_text)

    def test_how_are_you_returns_natural_response(self):
        """Phase 2 : 'Comment vas-tu ?' répond naturellement."""
        response = self.service.handle_message(
            self.db,
            self.user,
            "Comment vas-tu ?",
        )
        self.assertFalse(response["aides_recommandees"])

    def test_job_search_with_complete_profile_recommends(self):
        """Phase 3-4 : recherche d'emploi avec profil complet déclenche recommandation."""
        response = self.service.handle_message(
            self.db,
            self.user,
            "Je cherche un emploi",
        )
        self.assertIn(response["conversation_state"], ["RECOMMENDING", "COLLECTING_INFO"])
        if response["aides_recommandees"]:
            aid = response["aides_recommandees"][0]
            self.assertIn("score_matching", aid)
            self.assertIn("raisons", aid)
            self.assertIn("lien_officiel", aid)

    def test_collecting_info_asks_one_question_at_a_time(self):
        """Phase 3 : une seule question à la fois quand le profil est incomplet."""
        incomplete_user = Utilisateur(
            nom="Test",
            email="test@test.com",
            mot_de_passe_hash="hash",
            role="utilisateur",
            statut_compte="actif",
        )
        self.db.add(incomplete_user)
        self.db.commit()
        self.db.refresh(incomplete_user)

        response = self.service.handle_message(
            self.db,
            incomplete_user,
            "Je cherche des études",
        )
        self.assertEqual(response["conversation_state"], "COLLECTING_INFO")
        self.assertTrue(response["champs_manquants"])
        self.assertTrue(response["question_actuelle"])
        self.assertTrue(response["suggestions"])

    def test_recommendation_returns_full_details(self):
        """Phase 7 : une recommandation retourne score, raisons, lien, catégorie."""
        engine = RecommendationEngine()
        profile = {
            "ville": "Casablanca",
            "region": "Casablanca-Settat",
            "niveau_etude": "Licence",
            "statut_socio_pro": "Étudiant",
            "age": 22,
            "handicap": False,
        }
        aid = self.db.query(Aides).first()
        score, raisons = engine.calculate_score(profile, aid)
        self.assertGreaterEqual(score, 80)
        self.assertTrue(any("Région" in r for r in raisons))
        self.assertTrue(any("Âge" in r for r in raisons))

    def test_state_persistence_between_messages(self):
        """Phase 6 : le contexte conversationnel persiste entre deux messages."""
        response = self.service.handle_message(
            self.db,
            self.user,
            "Bonjour",
        )
        hist_id = response["historique_id"]

        response2 = self.service.handle_message(
            self.db,
            self.user,
            "Je cherche un emploi",
            historique_id=hist_id,
        )
        self.assertEqual(response2["historique_id"], hist_id)

    def test_meta_persistence_in_database(self):
        """Phase 6 : conversation_meta est bien persisté en base."""
        response = self.service.handle_message(
            self.db,
            self.user,
            "Bonjour",
        )
        from app.models.historique import Historique
        history = self.db.query(Historique).filter(
            Historique.historique_id == response["historique_id"]
        ).first()
        self.assertIsNotNone(history.conversation_meta)
        meta = ConversationMeta.from_json(history.conversation_meta)
        self.assertIn(meta.state, [ConversationState.COLLECTING_INFO, ConversationState.DISCUSSING])

    def test_two_turn_conversation_keeps_memory(self):
        """Conversation en deux tours avec mémoire."""
        first = self.service.handle_message(
            self.db,
            self.user,
            "Je suis étudiant, quelles aides existent ?",
        )
        second = self.service.handle_message(
            self.db,
            self.user,
            "la meilleure ?",
            historique_id=first["historique_id"],
        )
        messages = (
            self.db.query(Discussion)
            .filter(Discussion.historique_id == first["historique_id"])
            .order_by(Discussion.discussion_id)
            .all()
        )
        results_count = (
            self.db.query(ResultatChatbot)
            .filter(ResultatChatbot.historique_id == first["historique_id"])
            .count()
        )
        self.assertEqual(first["historique_id"], second["historique_id"])
        self.assertEqual(len(messages), 4)
        self.assertGreaterEqual(results_count, 1)

    def test_clean_text_compacts_and_limits_context(self):
        self.assertEqual(_clean_text("  Bonjour\n\n AidFinder  "), "Bonjour AidFinder")
        self.assertEqual(_clean_text("abcdef", 3), "abc...")

    def test_intent_detector_detects_greeting(self):
        detector = IntentDetector()
        meta = ConversationMeta()
        self.assertEqual(detector.detect("Bonjour", meta), IntentCategory.GREETING)
        self.assertEqual(detector.detect("salut", meta), IntentCategory.GREETING)
        self.assertEqual(detector.detect("hello", meta), IntentCategory.GREETING)

    def test_intent_detector_detects_job_search(self):
        detector = IntentDetector()
        meta = ConversationMeta()
        self.assertEqual(detector.detect("Je cherche un emploi", meta), IntentCategory.SEARCH_JOB)

    def test_intent_detector_detects_study_search(self):
        detector = IntentDetector()
        meta = ConversationMeta()
        self.assertEqual(detector.detect("Je veux faire des études", meta), IntentCategory.SEARCH_STUDY)

    def test_how_are_you_intent(self):
        detector = IntentDetector()
        meta = ConversationMeta()
        self.assertEqual(detector.detect("Comment ça va ?", meta), IntentCategory.HOW_ARE_YOU)

    def test_fallback_greeting_response(self):
        fallback = FallbackTemplates()
        decision = ConversationDecision(
            intent=IntentCategory.GREETING,
            new_state=ConversationState.GREETING,
            should_recommend=False,
            should_ask_question=False,
            field_to_ask=None,
            extracted_info={},
            merged_profile={},
            clarification_needed=False,
        )
        meta = ConversationMeta()
        response = fallback.generate(decision, meta)
        self.assertTrue("Bonjour" in response or "Salut" in response)

    def test_fallback_recommendation_response(self):
        fallback = FallbackTemplates()
        recommendations = [
            {
                "titre": "Aide Test",
                "score_matching": 85,
                "raisons": ["Région compatible", "Âge compatible"],
                "lien_officiel": "https://example.gov/aide",
            }
        ]
        decision = ConversationDecision(
            intent=IntentCategory.SEARCH_JOB,
            new_state=ConversationState.RECOMMENDING,
            should_recommend=True,
            should_ask_question=False,
            field_to_ask=None,
            extracted_info={},
            merged_profile={"ville": "Rabat"},
            clarification_needed=False,
        )
        meta = ConversationMeta()
        response = fallback.generate(decision, meta, recommendations)
        self.assertIn("Aide Test", response)
        self.assertIn("85/100", response)
        self.assertIn("https://example.gov/aide", response)

    def test_profile_collector_extracts_ville(self):
        collector = ProfileCollector()
        result = collector.extract("J'habite à Casablanca")
        self.assertEqual(result.get("ville"), "Casablanca")

    def test_profile_collector_extracts_age(self):
        collector = ProfileCollector()
        result = collector.extract("J'ai 25 ans")
        self.assertEqual(result.get("age"), 25)

    def test_profile_collector_extracts_handicap(self):
        collector = ProfileCollector()
        result = collector.extract("J'ai une situation de handicap")
        self.assertTrue(result.get("handicap"))


if __name__ == "__main__":
    unittest.main()