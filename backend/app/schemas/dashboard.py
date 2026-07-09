from datetime import datetime

from pydantic import BaseModel


class DashboardAidResponse(BaseModel):
    id: int
    aide_id: int
    titre: str
    description: str | None = None
    image: str | None = None
    image_url: str | None = None
    categorie: str | None = None
    url_officielle: str | None = None
    region_cible: str | None = None
    type_aide: str | None = None
    score_matching: int | None = None
    date_creation: datetime | None = None
    date_consultation: datetime | None = None


class DashboardConversationResponse(BaseModel):
    historique_id: int
    titre_resume: str
    dernier_message: str | None = None
    date_creation: datetime | None = None
    date_derniere_activite: datetime | None = None


class DashboardHistoryResponse(BaseModel):
    historique_id: int
    titre_resume: str
    nombre_messages: int
    nombre_recommandations: int
    dernier_message: str | None = None
    date_creation: datetime | None = None
    date_derniere_activite: datetime | None = None


class UserStatsResponse(BaseModel):
    nombre_recherches: int
    nombre_recommandations: int
    nombre_pdf_exportes: int
    nombre_conversations: int
    progression_profil: int


class UserDashboardResponse(BaseModel):
    nom_utilisateur: str
    photo: str | None = None
    progression_profil: int
    nombre_recherches: int
    nombre_recommandations: int
    nombre_pdf_exportes: int
    nombre_conversations: int
    dernieres_aides_consultees: list[DashboardAidResponse]
    dernieres_conversations: list[DashboardConversationResponse]
    aides_recommandees: list[DashboardAidResponse]
