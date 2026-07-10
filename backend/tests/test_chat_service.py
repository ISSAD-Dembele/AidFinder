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
from app.services.chat_service import ChatService, ChatContext, _clean_text


class FakeQwenClient:
    def __init__(self):
        self.calls = []

    def generate(self, messages):
        self.calls.append(messages)
        return "Réponse Qwen basée uniquement sur les aides fournies."


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
        self.service.qwen_client = self.fake_qwen

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_two_turn_conversation_keeps_memory_and_records_recommendations(self):
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
        second_prompt = self.fake_qwen.calls[1][1]["content"]

        self.assertEqual(first["historique_id"], second["historique_id"])
        self.assertEqual(len(messages), 4)
        self.assertGreaterEqual(results_count, 2)
        self.assertIn("Je suis étudiant", second_prompt)
        self.assertIn("la meilleure ?", second_prompt)
        self.assertIn("Bourse étudiant Casablanca", second_prompt)
        self.assertIn("https://example.gov/bourse", second_prompt)

    def test_fallback_answer_uses_best_aid_only(self):
        context = ChatContext(
            profile={"ville": "Rabat"},
            history=[],
            aids=[
                {
                    "aide_id": 1,
                    "titre": "Aide officielle",
                    "score_matching": 95,
                    "raisons": ["Région compatible"],
                    "lien_officiel": "https://example.gov/aide",
                }
            ],
        )

        answer = self.service._fallback_answer(context)

        self.assertIn("Aide officielle", answer)
        self.assertIn("95/100", answer)
        self.assertIn("https://example.gov/aide", answer)

    def test_clean_text_compacts_and_limits_context(self):
        self.assertEqual(_clean_text("  Bonjour\n\n AidFinder  "), "Bonjour AidFinder")
        self.assertEqual(_clean_text("abcdef", 3), "abc...")


if __name__ == "__main__":
    unittest.main()
