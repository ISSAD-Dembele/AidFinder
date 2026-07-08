from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.home import (
    HomeCategoryResponse,
    HomeLatestAidResponse,
    HomeSearchResultResponse,
    HomeStatsResponse,
)
from app.services.home_service import (
    get_home_categories,
    get_home_stats,
    get_latest_aids,
    search_home_aids,
)

router = APIRouter(
    prefix="/api/home",
    tags=["Accueil"],
)


@router.get(
    "/latest-aids",
    response_model=list[HomeLatestAidResponse],
    summary="Récupérer les dernières aides",
    description="Retourne les 6 aides les plus récentes enregistrées dans PostgreSQL.",
)
def read_latest_aids(db: Session = Depends(get_db)) -> list[HomeLatestAidResponse]:
    return get_latest_aids(db)


@router.get(
    "/stats",
    response_model=HomeStatsResponse,
    summary="Récupérer les statistiques de l'accueil",
    description="Calcule le nombre d'aides, le nombre de sources et la dernière mise à jour depuis PostgreSQL.",
)
def read_home_stats(db: Session = Depends(get_db)) -> HomeStatsResponse:
    return get_home_stats(db)


@router.get(
    "/categories",
    response_model=list[HomeCategoryResponse],
    summary="Récupérer les catégories d'aides",
    description="Liste les catégories existantes avec leur nombre d'aides associé.",
)
def read_home_categories(db: Session = Depends(get_db)) -> list[HomeCategoryResponse]:
    return get_home_categories(db)


@router.get(
    "/search",
    response_model=list[HomeSearchResultResponse],
    summary="Rechercher rapidement des aides",
    description="Recherche dans le titre et la description des aides, puis limite les résultats à 20.",
)
def search_aids(
    q: str = Query(..., min_length=1, description="Texte recherché dans le titre et la description."),
    db: Session = Depends(get_db),
) -> list[HomeSearchResultResponse]:
    return search_home_aids(db, q)
