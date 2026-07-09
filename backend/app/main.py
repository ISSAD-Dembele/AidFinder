from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.auth import router as auth_router
from app.routes.admin import router as admin_router
from app.routes.dashboard import router as dashboard_router
from app.routes.home import router as home_router
from app.routes.users import router as users_router
from app.core.config import CORS_ORIGINS, CORS_ORIGIN_REGEX
from fastapi.staticfiles import StaticFiles
import os, threading
from app.scraping.scheduler import start_scheduler
from app.database.database import Base, engine
from sqlalchemy import text

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(home_router)
app.include_router(dashboard_router)
app.include_router(dashboard_router, prefix="/api")
app.include_router(admin_router)
app.include_router(admin_router, prefix="/api")

os.makedirs("uploads/profiles", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
@app.get("/")
def home():
    return {"message": "Bienvenue sur AidFinder"}
@app.on_event("startup")
def startup_event():
    ensure_database_schema()
    threading.Thread(target=start_scheduler, daemon=True).start()


def ensure_database_schema():
    Base.metadata.create_all(bind=engine)
    ensure_runtime_columns()


def ensure_runtime_columns():
    if engine.dialect.name != "postgresql":
        return
    statements = (
        "ALTER TABLE aides ADD COLUMN IF NOT EXISTS est_active BOOLEAN NOT NULL DEFAULT TRUE",
        "ALTER TABLE utilisateurs ADD COLUMN IF NOT EXISTS date_derniere_connexion TIMESTAMP NULL",
    )
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
