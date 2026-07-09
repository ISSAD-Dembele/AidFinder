from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.securite import get_current_admin
from app.database.session import get_db
from app.models.utilisateurs import Utilisateur
from app.schemas.admin import (
    AdminAideCreate,
    AdminAideResponse,
    AdminAideUpdate,
    AdminDashboardStatsResponse,
    AdminLogsResponse,
    AdminSourceResponse,
    AdminSourceScrapeResponse,
    AdminStatsResponse,
    AdminUserResponse,
    AdminUserUpdate,
    MessageResponse,
)
from app.services.admin_service import (
    activate_user,
    create_aide,
    deactivate_user,
    delete_aide,
    delete_user,
    get_dashboard_stats,
    get_logs,
    get_statistics,
    get_user,
    list_aides,
    list_sources,
    list_users,
    rerun_source_scraping,
    set_aide_active,
    update_aide,
    update_user,
)

router = APIRouter(prefix="/admin", tags=["Administration"])


@router.get("/dashboard", response_model=AdminDashboardStatsResponse)
def read_admin_dashboard(
    _: Utilisateur = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminDashboardStatsResponse:
    return get_dashboard_stats(db)


@router.get("/utilisateurs", response_model=list[AdminUserResponse])
def read_users(
    _: Utilisateur = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[AdminUserResponse]:
    return list_users(db)


@router.get("/utilisateur/{user_id}", response_model=AdminUserResponse)
def read_user(
    user_id: int,
    _: Utilisateur = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminUserResponse:
    return get_user(db, user_id)


@router.put("/utilisateur/{user_id}", response_model=AdminUserResponse)
def edit_user(
    user_id: int,
    data: AdminUserUpdate,
    _: Utilisateur = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminUserResponse:
    return update_user(db, user_id, data)


@router.patch("/utilisateur/{user_id}/activer", response_model=AdminUserResponse)
def enable_user(
    user_id: int,
    _: Utilisateur = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminUserResponse:
    return activate_user(db, user_id)


@router.patch("/utilisateur/{user_id}/desactiver", response_model=AdminUserResponse)
def disable_user(
    user_id: int,
    _: Utilisateur = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminUserResponse:
    return deactivate_user(db, user_id)


@router.delete("/utilisateur/{user_id}", response_model=MessageResponse)
def remove_user(
    user_id: int,
    _: Utilisateur = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> MessageResponse:
    return delete_user(db, user_id)


@router.get("/aides", response_model=list[AdminAideResponse])
def read_aides(
    _: Utilisateur = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[AdminAideResponse]:
    return list_aides(db)


@router.post("/aides", response_model=AdminAideResponse)
def add_aide(
    data: AdminAideCreate,
    _: Utilisateur = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminAideResponse:
    return create_aide(db, data)


@router.put("/aides/{aide_id}", response_model=AdminAideResponse)
def edit_aide(
    aide_id: int,
    data: AdminAideUpdate,
    _: Utilisateur = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminAideResponse:
    return update_aide(db, aide_id, data)


@router.delete("/aides/{aide_id}", response_model=MessageResponse)
def remove_aide(
    aide_id: int,
    _: Utilisateur = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> MessageResponse:
    return delete_aide(db, aide_id)


@router.patch("/aides/{aide_id}/activer", response_model=AdminAideResponse)
def enable_aide(
    aide_id: int,
    _: Utilisateur = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminAideResponse:
    return set_aide_active(db, aide_id, True)


@router.patch("/aides/{aide_id}/desactiver", response_model=AdminAideResponse)
def disable_aide(
    aide_id: int,
    _: Utilisateur = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminAideResponse:
    return set_aide_active(db, aide_id, False)


@router.get("/sources", response_model=list[AdminSourceResponse])
def read_sources(
    _: Utilisateur = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[AdminSourceResponse]:
    return list_sources(db)


@router.post("/sources/{source_id}/scraping", response_model=AdminSourceScrapeResponse)
def restart_source_scraping(
    source_id: int,
    _: Utilisateur = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminSourceScrapeResponse:
    return rerun_source_scraping(db, source_id)


@router.get("/statistiques", response_model=AdminStatsResponse)
def read_statistics(
    _: Utilisateur = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminStatsResponse:
    return get_statistics(db)


@router.get("/logs", response_model=AdminLogsResponse)
def read_logs(
    _: Utilisateur = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminLogsResponse:
    return get_logs(db)
