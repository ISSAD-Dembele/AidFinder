from datetime import datetime

from pydantic import BaseModel, ConfigDict


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


class HomeStatsResponse(BaseModel):
    total_aides: int
    total_sources: int
    derniere_mise_a_jour: datetime | None = None


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
