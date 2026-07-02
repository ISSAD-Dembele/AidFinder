"""
Constantes des statuts de compte utilisateur.

Sépare clairement :
- la pause volontaire (desactive_utilisateur)
- la sanction administrative (suspendu_admin)

Cette séparation facilitera le futur Dashboard Administrateur
(suspension, réactivation, avertissements) sans refondre la logique.
"""

ACTIF = "actif"
DESACTIVE_UTILISATEUR = "desactive_utilisateur"
SUSPENDU_ADMIN = "suspendu_admin"

# Ancienne valeur — compatibilité avec les comptes déjà en base
LEGACY_DESACTIVE = "desactive"


def est_desactive_par_utilisateur(statut: str) -> bool:
    return statut in (DESACTIVE_UTILISATEUR, LEGACY_DESACTIVE)


def est_suspendu_par_admin(statut: str) -> bool:
    return statut == SUSPENDU_ADMIN
