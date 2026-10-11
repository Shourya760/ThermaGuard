"""
app/main.py

Entry point for the CoolBlock FastAPI application.
CORS origins are read from settings (app/core/config.py) so they can be
changed via the .env file without touching application code.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes.weather import router as weather_router
from app.routes.zones import router as zones_router
from app.routes.risk import router as risk_router
from app.routes.scenarios import router as scenarios_router
from app.routes.plans import router as plans_router
from app.db.session import engine
from app.db.models import Base

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CoolBlock API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(weather_router)
app.include_router(zones_router)
app.include_router(risk_router)
app.include_router(scenarios_router)
app.include_router(plans_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to CoolBlock API"}


@app.get("/api/health")
def health_check():
    return {"status": "ok", "env": settings.app_env}
