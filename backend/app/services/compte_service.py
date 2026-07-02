"""
Opérations sur le statut de compte — prêtes pour le futur Dashboard Administrateur.

Les routes admin consommeront ces fonctions (suspension, réactivation, avertissements)
sans dupliquer la logique métier.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.statuts_compte import ACTIF, SUSPENDU_ADMIN
from app.models.utilisateurs import Utilisateur


def suspendre_par_admin(db: Session, utilisateur: Utilisateur) -> Utilisateur:
    """Suspend un compte — réservé au Dashboard Administrateur."""
    utilisateur.statut_compte = SUSPENDU_ADMIN
    utilisateur.date_desactivation = datetime.now(timezone.utc)
    db.commit()
    db.refresh(utilisateur)
    return utilisateur


def reactiver_par_admin(db: Session, utilisateur: Utilisateur) -> Utilisateur:
    """Réactive un compte suspendu par un administrateur."""
    utilisateur.statut_compte = ACTIF
    utilisateur.date_desactivation = None
    db.commit()
    db.refresh(utilisateur)
    return utilisateur
