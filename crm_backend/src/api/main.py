from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.config import get_settings
from src.db.session import engine
from src.db.init_db import init_db

# Routers
from src.api.routers_auth import router as auth_router
from src.api.routers_clients import router as clients_router
from src.api.routers_leads import router as leads_router
from src.api.routers_activities import router as activities_router
from src.api.routers_communications import router as communications_router
from src.api.routers_metrics import router as metrics_router

settings = get_settings()

app = FastAPI(
    title="Finance CRM Backend",
    description="Backend API for the Finance CRM application. Provides authentication, data operations, and integrations.",
    version="0.1.0",
    contact={"name": "Finance CRM", "url": "https://example.com"},
    license_info={"name": "Proprietary"},
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS settings driven by environment variables for flexibility.
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.CORS_ALLOW_ORIGINS),
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=list(settings.CORS_ALLOW_METHODS),
    allow_headers=list(settings.CORS_ALLOW_HEADERS),
)

# Ensure database tables exist even if application startup events are not
# triggered (e.g., certain test runners or tooling that instantiate the app
# without running lifespan hooks). This call is idempotent.
init_db(engine)


@app.on_event("startup")
def on_startup() -> None:
    """Initialize application dependencies on startup.

    - Initialize database (create tables if they do not exist)
    """
    init_db(engine)


# PUBLIC_INTERFACE
@app.get("/", summary="Health Check", tags=["Health"])
def health_check() -> dict:
    """Health probe endpoint.

    Returns:
        dict: A simple status message to indicate the service is running.
    """
    return {"message": "Healthy"}


# Include API routers under /api/v1
app.include_router(auth_router)
app.include_router(clients_router)
app.include_router(leads_router)
app.include_router(activities_router)
app.include_router(communications_router)
app.include_router(metrics_router)
