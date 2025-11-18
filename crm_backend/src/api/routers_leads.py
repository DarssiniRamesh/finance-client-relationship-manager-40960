from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.api.schemas import LeadCreate, LeadOut, LeadUpdate, LeadTransition, LeadPage
from src.api.security import get_current_user
from src.db.models import Lead, User
from src.db.session import get_db

router = APIRouter(prefix="/api/v1/leads", tags=["Leads"])

VALID_STATUSES = {"new", "contacted", "qualified", "proposal", "won", "lost"}


def _paginate(query, page: int, page_size: int):
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return total, items


# PUBLIC_INTERFACE
@router.get("/", response_model=LeadPage, summary="List leads", description="List leads with optional search and pagination.")
def list_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    search: Optional[str] = Query(None, description="Search by title"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> LeadPage:
    """List leads with pagination and simple search."""
    q = db.query(Lead)
    if search:
        like = f"%{search.lower()}%"
        q = q.filter(func.lower(Lead.title).like(like))
    if status:
        q = q.filter(Lead.status == status)
    total, items = _paginate(q.order_by(Lead.created_at.desc()), page, page_size)
    return LeadPage(meta={"page": page, "page_size": page_size, "total": total}, results=[LeadOut.model_validate(i) for i in items])


# PUBLIC_INTERFACE
@router.post("/", response_model=LeadOut, status_code=201, summary="Create lead")
def create_lead(payload: LeadCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> LeadOut:
    """Create a lead."""
    if payload.status and payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")
    lead = Lead(
        title=payload.title,
        status=payload.status or "new",
        value=payload.value,
        client_id=payload.client_id,
        owner_id=payload.owner_id,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return LeadOut.model_validate(lead)


# PUBLIC_INTERFACE
@router.get("/{lead_id}", response_model=LeadOut, summary="Get lead")
def get_lead(lead_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> LeadOut:
    """Get a lead by id."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadOut.model_validate(lead)


# PUBLIC_INTERFACE
@router.put("/{lead_id}", response_model=LeadOut, summary="Update lead")
def update_lead(lead_id: int, payload: LeadUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> LeadOut:
    """Update lead fields."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    to_update = payload.model_dump(exclude_unset=True)
    if "status" in to_update and to_update["status"] and to_update["status"] not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")
    for field, value in to_update.items():
        setattr(lead, field, value)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return LeadOut.model_validate(lead)


# PUBLIC_INTERFACE
@router.post("/{lead_id}/transition", response_model=LeadOut, summary="Transition lead")
def transition_lead(lead_id: int, body: LeadTransition, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> LeadOut:
    """Change the lead status to a new valid state."""
    if body.to_status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead.status = body.to_status
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return LeadOut.model_validate(lead)


# PUBLIC_INTERFACE
@router.delete("/{lead_id}", status_code=204, summary="Delete lead")
def delete_lead(lead_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> None:
    """Delete lead by id.

    Returns no content (204) and thus no response body or model.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    db.delete(lead)
    db.commit()
    return None
