"""Constantes des statuts de compte utilisateur."""

ACTIF = "actif"
SUSPENDU = "suspendu"
DESACTIVE_UTILISATEUR = "desactive_utilisateur"


def est_suspendu(statut: str) -> bool:
    return statut == SUSPENDU

def est_desactive(statut: str) -> bool:
    return statut == DESACTIVE_UTILISATEUR
