from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.schemas import MetricsOut
from src.api.security import get_current_user
from src.db.models import Client, Lead, Activity, Communication, User
from src.db.session import get_db

router = APIRouter(prefix="/api/v1/metrics", tags=["Metrics"])


# PUBLIC_INTERFACE
@router.get("/", response_model=MetricsOut, summary="Get basic entity counts", description="Return counts of clients, leads, activities, and communications.")
def get_metrics(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> MetricsOut:
    """Return basic counts for dashboard metrics."""
    return MetricsOut(
        clients=db.query(Client).count(),
        leads=db.query(Lead).count(),
        activities=db.query(Activity).count(),
        communications=db.query(Communication).count(),
    )
