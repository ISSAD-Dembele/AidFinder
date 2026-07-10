from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.securite import get_current_user
from app.database.session import get_db
from app.models.utilisateurs import Utilisateur
from app.models.historique import Historique
from app.models.discussion import Discussion
from app.core.datetime_utils import as_utc, utc_now
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


class ChatMessageRequest(BaseModel):
    historique_id: Optional[int] = None
    message: str


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


@router.post("/chat")
def send_chat_message(
    data: ChatMessageRequest,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not data.message or not data.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le message ne peut pas être vide."
        )

    # 1. Récupérer ou créer l'historique
    if data.historique_id:
        history_item = db.query(Historique).filter(
            Historique.historique_id == data.historique_id,
            Historique.user_id == current_user.user_id
        ).first()
        if not history_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Discussion introuvable.",
            )
    else:
        # Création d'un nouvel historique
        title = data.message[:40].strip() + ("..." if len(data.message) > 40 else "")
        history_item = Historique(
            user_id=current_user.user_id,
            titre_resume=title
        )
    
    try:
        if not data.historique_id:
            db.add(history_item)
            db.flush()

        # 2. Enregistrer le message de l'utilisateur
        user_msg = Discussion(
            historique_id=history_item.historique_id,
            expediteur="user",
            contenu=data.message
        )
        db.add(user_msg)
        
        # 3. Simuler et enregistrer la réponse du chatbot
        region = current_user.region or "non renseignée"
        etude = current_user.niveau_etude or "sans diplôme"
        bot_text = f"Merci pour votre demande : \"{data.message}\". Notre assistant analyse actuellement votre profil ({region}, {etude}) afin de vous proposer les meilleures aides d'État éligibles. Cette fonctionnalité sera entièrement connectée au modèle IA dans la prochaine version."
        
        bot_msg = Discussion(
            historique_id=history_item.historique_id,
            expediteur="assistant",
            contenu=bot_text
        )
        db.add(bot_msg)
        
        # 4. Mettre à jour la date de dernière activité
        history_item.date_derniere_activite = utc_now()
        db.commit()
        db.refresh(user_msg)
        db.refresh(bot_msg)
        db.refresh(history_item)
    except Exception:
        db.rollback()
        raise
    
    return {
        "historique_id": history_item.historique_id,
        "titre_resume": history_item.titre_resume,
        "date_derniere_activite": as_utc(history_item.date_derniere_activite),
        "user_message": {
            "discussion_id": user_msg.discussion_id,
            "expediteur": "user",
            "contenu": data.message,
            "date_creation": as_utc(user_msg.date_creation),
        },
        "bot_message": {
            "discussion_id": bot_msg.discussion_id,
            "expediteur": "assistant",
            "contenu": bot_text,
            "date_creation": as_utc(bot_msg.date_creation),
        }
    }


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
