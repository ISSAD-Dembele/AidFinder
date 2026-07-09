from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.securite import get_current_user
from app.database.session import get_db
from app.models.utilisateurs import Utilisateur
from app.schemas.dashboard import (
    DashboardAidResponse,
    DashboardHistoryResponse,
    UserDashboardResponse,
    UserStatsResponse,
)
from app.services.dashboard_service import (
    get_recent_aids,
    get_user_dashboard,
    get_user_history,
    get_user_recommendations,
    get_user_stats,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard utilisateur"])


@router.get("", response_model=UserDashboardResponse)
def read_dashboard(
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserDashboardResponse:
    return get_user_dashboard(db, current_user)


@router.get("/history", response_model=list[DashboardHistoryResponse])
def read_history(
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[DashboardHistoryResponse]:
    return get_user_history(db, current_user)


@router.get("/recommendations", response_model=list[DashboardAidResponse])
def read_recommendations(
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[DashboardAidResponse]:
    return get_user_recommendations(db, current_user)


@router.get("/recent-aids", response_model=list[DashboardAidResponse])
def read_recent_aids(
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[DashboardAidResponse]:
    return get_recent_aids(db, current_user)


@router.get("/stats", response_model=UserStatsResponse)
def read_stats(
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserStatsResponse:
    return get_user_stats(db, current_user)
