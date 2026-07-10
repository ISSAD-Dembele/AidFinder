from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_serializer

from app.core.datetime_utils import as_utc


class HomeLatestAidResponse(BaseModel):
    aide_id: int
    titre: str
    description: str | None = None
    image_url: str | None = None
    region_cible: str | None = None
    type_aide: str | None = None
    url_officielle: str | None = None
    date_creation: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("date_creation")
    def serialize_datetime(self, value: datetime | None):
        return as_utc(value)


class HomeStatsResponse(BaseModel):
    total_aides: int
    total_categories: int
    total_sources: int
    total_utilisateurs: int
    total_conversations: int
    derniere_mise_a_jour: datetime | None = None

    @field_serializer("derniere_mise_a_jour")
    def serialize_datetime(self, value: datetime | None):
        return as_utc(value)


class HomeCategoryResponse(BaseModel):
    id: int
    nom: str
    description: str | None = None
    nombre_aides: int


class HomeSearchResultResponse(BaseModel):
    aide_id: int
    titre: str
    description: str | None = None
    image_url: str | None = None
    region_cible: str | None = None
    type_aide: str | None = None
    url_officielle: str | None = None
    date_creation: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("date_creation")
    def serialize_datetime(self, value: datetime | None):
        return as_utc(value)
