"""Constantes des statuts de compte utilisateur."""

ACTIF = "actif"
SUSPENDU = "suspendu"


def est_suspendu(statut: str) -> bool:
    return statut == SUSPENDU
