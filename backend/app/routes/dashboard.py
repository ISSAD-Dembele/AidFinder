from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.securite import get_current_user
from app.database.session import get_db
from app.models.utilisateurs import Utilisateur
from app.models.historique import Historique
from app.models.discussion import Discussion
from app.core.datetime_utils import as_utc
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse
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
from app.services.chat_service import chat_service

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


@router.get("/history/{history_id}")
def read_history_detail(
    history_id: int,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    history_item = db.query(Historique).filter(
        Historique.historique_id == history_id,
        Historique.user_id == current_user.user_id
    ).first()
    if not history_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion introuvable.",
        )
    discussions = db.query(Discussion).filter(
        Discussion.historique_id == history_id
    ).order_by(Discussion.date_creation).all()
    
    return {
        "historique_id": history_item.historique_id,
        "titre_resume": history_item.titre_resume,
        "date_creation": as_utc(history_item.date_creation),
        "messages": [
            {
                "discussion_id": d.discussion_id,
                "expediteur": d.expediteur,
                "contenu": d.contenu,
                "date_creation": as_utc(d.date_creation)
            }
            for d in discussions
        ]
    }


@router.post("/chat", response_model=ChatMessageResponse)
def send_chat_message(
    data: ChatMessageRequest,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatMessageResponse:
    return chat_service.handle_message(
        db=db,
        user=current_user,
        message=data.message,
        historique_id=data.historique_id,
    )


@router.delete("/history/{history_id}")
def delete_history_entry(
    history_id: int,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    history_item = db.query(Historique).filter(
        Historique.historique_id == history_id,
        Historique.user_id == current_user.user_id
    ).first()
    if not history_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discussion introuvable.",
        )
    db.delete(history_item)
    db.commit()
    return {"message": "Discussion supprimée avec succès."}


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
