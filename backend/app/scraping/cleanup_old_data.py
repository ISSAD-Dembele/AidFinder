"""
Script de nettoyage : supprime toutes les aides provenant
de l'ancien scraper emploi basé sur www.anapec.org.

Les anciennes données sont identifiables par :
  - url_officielle contenant "www.anapec.org" ou "sigec-app-rv"
  - source_nom = "ANAPEC" ET categorie_nom = "Offres d'emploi"
    ET url_officielle ne commençant PAS par "https://anapec.ma/chercheurs/offres"

Exécution : python -m app.scraping.cleanup_old_data
"""

import sys
import os

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from app.database.database import SessionLocal
from app.models.aides import Aides
from app.models.source_aide import SourceAide
from app.models.categorie_aide import CategorieAide
from app.models.scraping_logs import ScrapingLog


def cleanup_old_emploi_data():
    """Supprime toutes les données provenant de l'ancien scraper www.anapec.org."""
    db = SessionLocal()
    try:
        # Identifier les aides à supprimer :
        # Celles dont l'url_officielle contient www.anapec.org ou sigec-app-rv
        # (ancien scraper) mais PAS les nouvelles qui pointent vers anapec.ma
        old_aides = (
            db.query(Aides)
            .filter(
                Aides.url_officielle.notlike("https://anapec.ma/chercheurs/offres%")
            )
            .filter(
                Aides.url_officielle.like("%www.anapec.org%")
                | Aides.url_officielle.like("%sigec-app-rv%")
            )
            .all()
        )

        count = len(old_aides)
        print(f"[CLEANUP] {count} aides à supprimer (ancien scraper www.anapec.org)")

        if count == 0:
            print("[CLEANUP] Aucune donnée à nettoyer.")
            return

        # Supprimer les aides
        for aide in old_aides:
            db.delete(aide)

        db.commit()
        print(f"[CLEANUP] {count} aides supprimées avec succès.")

        # Nettoyer les logs de scraping obsolètes
        old_logs = (
            db.query(ScrapingLog)
            .filter(ScrapingLog.source.like("%anapec_emploi%"))
            .all()
        )
        log_count = len(old_logs)
        for log in old_logs:
            db.delete(log)
        db.commit()
        print(f"[CLEANUP] {log_count} logs de scraping supprimés.")

    except Exception as e:
        db.rollback()
        print(f"[CLEANUP] Erreur : {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    cleanup_old_emploi_data()