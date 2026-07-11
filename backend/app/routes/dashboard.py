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
    record_aid_consultation,
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
    
    # Charger l'état complet du chatbot pour restaurer la conversation au rechargement
    from app.services.conversation_engine import ConversationMeta
    from app.services.chat_service import _build_user_profile, chat_service
    from app.services.dashboard_service import calculate_recommendation_score, _serialize_aid
    from app.models.resultat_chat import ResultatChatbot
    
    meta = ConversationMeta.from_json(history_item.conversation_meta)
    db_profile = _build_user_profile(current_user)
    merged_profile = dict(db_profile)
    merged_profile.update(meta.collected_fields)
    
    missing_fields = chat_service.brain.profile_collector.missing_fields(merged_profile)
    field_to_ask = chat_service.brain.profile_collector.next_missing_field(merged_profile)
    
    question = None
    suggestions = []
    if meta.state == "COLLECTING_INFO" and field_to_ask:
        question = chat_service.brain.profile_collector.get_question(field_to_ask)
        suggestions = chat_service.brain.profile_collector.get_suggestions(field_to_ask)
        
    resultats = db.query(ResultatChatbot).filter(
        ResultatChatbot.historique_id == history_id
    ).all()
    
    aides_recommandees = []
    for r in resultats:
        score, raisons = calculate_recommendation_score(current_user, r.aide)
        aides_recommandees.append(_serialize_aid(r.aide, score_matching=score, raisons=raisons))
    
    return {
        "historique_id": history_item.historique_id,
        "titre_resume": history_item.titre_resume,
        "date_creation": as_utc(history_item.date_creation),
        "conversation_state": meta.state.value if meta.state else "GREETING",
        "champs_manquants": missing_fields,
        "question_actuelle": question,
        "suggestions": suggestions,
        "aides_recommandees": aides_recommandees,
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


@router.post("/chat/{historique_id}/consultation/{aide_id}", response_model=dict)
def record_chat_consultation(
    historique_id: int,
    aide_id: int,
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    consultation = record_aid_consultation(db, current_user, aide_id)
    return {
        "message": "Consultation enregistrée avec succès.",
        "consultation_id": consultation.id,
        "aide_id": aide_id,
    }


@router.get("/stats", response_model=UserStatsResponse)
def read_stats(
    current_user: Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserStatsResponse:
    return get_user_stats(db, current_user)
