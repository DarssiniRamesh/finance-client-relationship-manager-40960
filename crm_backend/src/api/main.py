from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.config import get_settings
from src.db.session import engine
from src.db.init_db import init_db

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
