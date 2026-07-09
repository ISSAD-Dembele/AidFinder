from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class AdminDashboardStatsResponse(BaseModel):
    total_utilisateurs: int
    total_aides: int
    total_categories: int
    total_sources: int
    total_conversations: int
    total_pdf_exportes: int
    comptes_actifs: int
    comptes_desactives: int


class AdminUserResponse(BaseModel):
    user_id: int
    nom: str
    email: EmailStr
    role: str
    statut_compte: str
    date_naissance: date | None = None
    region: str | None = None
    niveau_etude: str | None = None
    statut_socio_pro: str | None = None
    situation_handicap: bool | None = None
    photo_profil: str | None = None
    date_creation: datetime | None = None
    date_derniere_connexion: datetime | None = None
    date_desactivation: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class AdminUserUpdate(BaseModel):
    nom: str | None = None
    email: EmailStr | None = None
    role: str | None = None
    statut_compte: str | None = None
    date_naissance: date | None = None
    region: str | None = None
    niveau_etude: str | None = None
    statut_socio_pro: str | None = None
    situation_handicap: bool | None = None


class AdminAideBase(BaseModel):
    source_id: int
    categorie_id: int
    titre: str
    description: str | None = None
    date_limite: date | None = None
    type_aide: str | None = None
    montant: float | None = None
    age_min: int | None = None
    age_max: int | None = None
    region_cible: str | None = None
    niveau_etude_requis: str | None = None
    statut_socio_pro_requis: str | None = None
    handicap_requis: bool | None = None
    url_officielle: str | None = None
    image_url: str | None = None
    est_active: bool = True


class AdminAideCreate(AdminAideBase):
    pass


class AdminAideUpdate(BaseModel):
    source_id: int | None = None
    categorie_id: int | None = None
    titre: str | None = None
    description: str | None = None
    date_limite: date | None = None
    type_aide: str | None = None
    montant: float | None = None
    age_min: int | None = None
    age_max: int | None = None
    region_cible: str | None = None
    niveau_etude_requis: str | None = None
    statut_socio_pro_requis: str | None = None
    handicap_requis: bool | None = None
    url_officielle: str | None = None
    image_url: str | None = None
    est_active: bool | None = None


class AdminAideResponse(AdminAideBase):
    aide_id: int
    source_id: int | None = None
    categorie_id: int | None = None
    categorie: str | None = None
    source: str | None = None
    date_creation: datetime | None = None
    derniere_mise_a_jour: datetime | None = None


class AdminSourceResponse(BaseModel):
    source_id: int
    nom: str
    url: str | None = None
    type_source: str | None = None
    est_fiable: bool
    fiabilite: str
    nombre_aides: int
    dernier_scraping: datetime | None = None
    statut: str


class AdminSourceScrapeResponse(BaseModel):
    message: str
    source_id: int
    source: str
    records: int
    dernier_scraping: datetime | None = None


class StatItem(BaseModel):
    label: str
    total: int


class EvolutionItem(BaseModel):
    date: date
    total: int


class AdminStatsResponse(BaseModel):
    aides_par_categorie: list[StatItem]
    aides_par_region: list[StatItem]
    evolution_utilisateurs: list[EvolutionItem]
    evolution_conversations: list[EvolutionItem]
    sources_les_plus_utilisees: list[StatItem]


class AdminScrapeLogResponse(BaseModel):
    scraplogs_id: int
    source: str
    started_at: datetime
    finished_at: datetime
    duration: str
    new_records: int
    updated_records: int
    expired_records: int
    status: str
    error_message: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class AdminConnectionLogResponse(BaseModel):
    user_id: int
    nom: str
    email: EmailStr
    role: str
    date_derniere_connexion: datetime | None = None


class AdminLogsResponse(BaseModel):
    derniers_scrapes: list[AdminScrapeLogResponse]
    dernieres_erreurs: list[AdminScrapeLogResponse]
    dernieres_connexions: list[AdminConnectionLogResponse]


class MessageResponse(BaseModel):
    message: str
