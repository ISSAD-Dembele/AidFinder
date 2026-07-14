from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.securite import get_current_admin
from app.database.session import get_db
from app.models.utilisateurs import Utilisateur
from app.schemas.admin import (
    AdminAideCreate,
    AdminAideResponse,
    AdminDashboardStatsResponse,
    AdminLogsResponse,
    AdminSourceResponse,
    AdminSourceScrapeResponse,
    AdminStatsResponse,
    AdminUserResponse,
    AdminWarningCreate,
    AdminWarningResponse,
    MessageResponse,
)
from app.services.admin_service import (
    create_aide,
    delete_aide,
    get_dashboard_stats,
    get_logs,
    get_statistics,
    get_user,
    list_aides,
    list_sources,
    list_users,
    list_warnings,
    rerun_source_scraping,
    set_aide_active,
    send_warning,
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


@router.post("/utilisateur/{user_id}/avertissements", response_model=AdminWarningResponse)
def create_warning(
    user_id: int,
    data: AdminWarningCreate,
    admin: Utilisateur = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminWarningResponse:
    warning, suspension_declenchee = send_warning(db, admin, user_id, data)
    return AdminWarningResponse(
        action_id=warning.action_id,
        motif=warning.motif,
        message_conversation=warning.message_conversation,
        date_creation=warning.date_creation,
        nombre_avertissements=warning.utilisateur.nombre_avertissements,
        suspension_declenchee=suspension_declenchee,
    )


@router.get("/utilisateur/{user_id}/avertissements", response_model=list[AdminWarningResponse])
def read_warnings(
    user_id: int,
    _: Utilisateur = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[AdminWarningResponse]:
    warnings = list_warnings(db, user_id)
    return [
        AdminWarningResponse(
            action_id=warning.action_id,
            motif=warning.motif,
            message_conversation=warning.message_conversation,
            date_creation=warning.date_creation,
            nombre_avertissements=index,
            suspension_declenchee=index >= 2,
        )
        for index, warning in enumerate(reversed(warnings), start=1)
    ][::-1]


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
