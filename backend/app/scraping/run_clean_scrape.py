"""
Script complet :
1. Nettoie les anciennes données anapec.org
2. Lance le nouveau scraper anapec.ma/chercheurs/offres
3. Sauvegarde les résultats
4. Vérifie la base
"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.database.database import SessionLocal
from app.models.aides import Aides
from app.models.scraping_logs import ScrapingLog
from app.scraping.sources.anapec.emploi import scrape_emploi
from app.scraping.storage import save_records
from sqlalchemy import text


def step1_cleanup():
    """Étape 1 : Supprimer les aides de l'ancien scraper www.anapec.org"""
    print("\n" + "=" * 60)
    print("[ÉTAPE 1] Nettoyage des données de l'ancien scraper www.anapec.org")
    print("=" * 60)

    db = SessionLocal()
    try:
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
        print(f"[CLEANUP] {count} aides à supprimer")
        for aide in old_aides:
            db.delete(aide)
        db.commit()
        print(f"[CLEANUP] {count} aides supprimées")

        # Nettoyer les logs
        old_logs = (
            db.query(ScrapingLog)
            .filter(ScrapingLog.source.like("%anapec_emploi%"))
            .all()
        )
        log_count = len(old_logs)
        for log in old_logs:
            db.delete(log)
        db.commit()
        print(f"[CLEANUP] {log_count} logs supprimés")
    except Exception as e:
        db.rollback()
        print(f"[CLEANUP] Erreur : {e}")
    finally:
        db.close()


def step2_verify_clean():
    """Étape 2 : Vérifier que plus aucune ligne de l'ancien scraper"""
    print("\n" + "=" * 60)
    print("[ÉTAPE 2] Vérification dans PostgreSQL : 0 ligne de l'ancien scraper ?")
    print("=" * 60)

    db = SessionLocal()
    try:
        count = db.execute(
            text(
                "SELECT COUNT(*) FROM aides "
                "WHERE url_officielle LIKE '%www.anapec.org%' "
                "OR url_officielle LIKE '%sigec-app-rv%'"
            )
        ).scalar()
        total = db.execute(text("SELECT COUNT(*) FROM aides")).scalar()
        print(f"[VERIF] Aides avec www.anapec.org ou sigec-app-rv : {count}")
        print(f"[VERIF] Total aides restantes : {total}")
        assert count == 0, f"Erreur : {count} lignes résiduelles détectées !"
        print("[VERIF] ✅ Base propre : aucune ligne résiduelle.")
    finally:
        db.close()


def step3_scrape():
    """Étape 3 : Lancer le nouveau scraper"""
    print("\n" + "=" * 60)
    print(
        "[ÉTAPE 3] Lancement du nouveau scraper anapec.ma/chercheurs/offres"
    )
    print("=" * 60)

    start = datetime.now()
    records = scrape_emploi()
    elapsed = (datetime.now() - start).total_seconds()

    print(f"\n[SCRAPE] Temps : {elapsed:.1f}s")
    print(f"[SCRAPE] Enregistrements récupérés : {len(records)}")

    if records:
        print(f"\n[SAVE] Sauvegarde de {len(records)} enregistrements...")
        save_records(records)
        print("[SAVE] ✅ Sauvegarde terminée.")
    else:
        print("[SCRAPE] ⚠️  Aucun enregistrement récupéré.")

    return records


def step4_show_logs(records):
    """Étape 4 : Afficher les logs complets et les premières lignes"""
    print("\n" + "=" * 60)
    print("[ÉTAPE 4] Résultats du nouveau scraping")
    print("=" * 60)

    if records:
        print(f"\n📋 {len(records)} offres d'emploi récupérées depuis "
              f"https://anapec.ma/chercheurs/offres")
        print(f"\n{'─' * 80}")
        print(f"{'#':<4} {'TITRE':<50} {'URL_OFFICIELLE'}")
        print(f"{'─' * 80}")

        for i, rec in enumerate(records, 1):
            titre = (rec.get("titre") or "")[:48]
            url = rec.get("url_officielle") or ""
            print(f"{i:<4} {titre:<50} {url}")

        # Vérification : url_officielle ne contient PAS www.anapec.org
        bad = [
            r
            for r in records
            if "www.anapec.org" in (r.get("url_officielle") or "")
        ]
        print(f"\n{'─' * 80}")
        print(f"[VERIF] Enregistrements avec www.anapec.org : {len(bad)} "
              f"(attendu: 0) ✅" if not bad else f"(attendu: 0) ❌")
        if bad:
            for r in bad:
                print(f"  ❌ {r.get('url_officielle')}")

        # Afficher les logs de scraping en base
        db = SessionLocal()
        try:
            logs = db.execute(
                text(
                    "SELECT source, status, new_records, duration, "
                    "started_at, finished_at, error_message "
                    "FROM scraping_logs "
                    "ORDER BY started_at DESC LIMIT 5"
                )
            ).fetchall()
            print(f"\n📜 Derniers logs de scraping :")
            for log in logs:
                print(f"  [{log[1]:>7}] {log[0]:<30} "
                      f"| {log[2]} enreg. | {log[3]}")
        finally:
            db.close()

    else:
        print("[RÉSULTAT] ⚠️  Aucune donnée à afficher.")


def step5_verify_db():
    """Étape 5 : Vérification finale en base"""
    print("\n" + "=" * 60)
    print("[ÉTAPE 5] Vérification finale en base de données")
    print("=" * 60)

    db = SessionLocal()
    try:
        rows = db.execute(
            text(
                "SELECT a.aide_id, a.titre, a.url_officielle, "
                "a.date_creation "
                "FROM aides a "
                "WHERE a.url_officielle LIKE '%anapec.ma%' "
                "ORDER BY a.aide_id DESC LIMIT 10"
            )
        ).fetchall()

        print(f"\n📋 Dernières aides insérées (anapec.ma) :")
        print(f"{'─' * 80}")
        print(f"{'ID':<5} {'TITRE':<50} {'URL_OFFICIELLE'}")
        print(f"{'─' * 80}")

        for r in rows:
            aide_id, titre, url, date_crea = r
            print(
                f"{aide_id:<5} {(titre or '')[:48]:<50} {url or ''}"
            )

        total = db.execute(text("SELECT COUNT(*) FROM aides")).scalar()
        print(f"\n[DB] Total aides en base : {total}")

        # Vérification finale : zéro ligne avec www.anapec.org
        anapec_org = db.execute(
            text(
                "SELECT COUNT(*) FROM aides "
                "WHERE url_officielle LIKE '%www.anapec.org%' "
                "OR url_officielle LIKE '%sigec-app-rv%'"
            )
        ).scalar()
        print(f"[DB] Lignes résiduelles www.anapec.org/sigec-app-rv : "
              f"{anapec_org} ✅" if anapec_org == 0 else
              f"{anapec_org} ❌ (doit être 0)")
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("🧹  NETTOYAGE COMPLET + NOUVEAU SCRAPING ANAPEC")
    print("=" * 60)

    step1_cleanup()
    step2_verify_clean()
    records = step3_scrape()
    step4_show_logs(records)
    step5_verify_db()

    print("\n" + "=" * 60)
    print("✅  PROCESSUS TERMINÉ")
    print("=" * 60)