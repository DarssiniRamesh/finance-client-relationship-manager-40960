from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.api.schemas import CommunicationCreate, CommunicationOut, CommunicationUpdate, CommunicationPage
from src.api.security import get_current_user
from src.db.models import Communication, Client, User
from src.db.session import get_db

router = APIRouter(prefix="/api/v1/communications", tags=["Communications"])


def _paginate(query, page: int, page_size: int):
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return total, items


# PUBLIC_INTERFACE
@router.get("/", response_model=CommunicationPage, summary="List communications")
def list_communications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    client_id: Optional[int] = Query(None, description="Filter by client id"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CommunicationPage:
    """List communications with optional filter by client."""
    q = db.query(Communication)
    if client_id:
        q = q.filter(Communication.client_id == client_id)
    total, items = _paginate(q.order_by(Communication.created_at.desc()), page, page_size)
    return CommunicationPage(
        meta={"page": page, "page_size": page_size, "total": total},
        results=[CommunicationOut.model_validate(i) for i in items],
    )


# PUBLIC_INTERFACE
@router.post("/", response_model=CommunicationOut, status_code=201, summary="Create communication")
def create_communication(
    payload: CommunicationCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> CommunicationOut:
    """Create a communication linked to a client."""
    client = db.query(Client).filter(Client.id == payload.client_id).first()
    if not client:
        raise HTTPException(status_code=400, detail="Client not found")
    comm = Communication(
        channel=payload.channel or "other",
        subject=payload.subject,
        content=payload.content,
        user_id=payload.user_id,
        client_id=payload.client_id,
    )
    db.add(comm)
    db.commit()
    db.refresh(comm)
    return CommunicationOut.model_validate(comm)


# PUBLIC_INTERFACE
@router.get("/{communication_id}", response_model=CommunicationOut, summary="Get communication")
def get_communication(communication_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> CommunicationOut:
    """Get a communication by id."""
    comm = db.query(Communication).filter(Communication.id == communication_id).first()
    if not comm:
        raise HTTPException(status_code=404, detail="Communication not found")
    return CommunicationOut.model_validate(comm)


# PUBLIC_INTERFACE
@router.put("/{communication_id}", response_model=CommunicationOut, summary="Update communication")
def update_communication(
    communication_id: int, payload: CommunicationUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> CommunicationOut:
    """Update a communication."""
    comm = db.query(Communication).filter(Communication.id == communication_id).first()
    if not comm:
        raise HTTPException(status_code=404, detail="Communication not found")

    data = payload.model_dump(exclude_unset=True)
    if "client_id" in data and data["client_id"] is not None:
        client = db.query(Client).filter(Client.id == data["client_id"]).first()
        if not client:
            raise HTTPException(status_code=400, detail="Client not found")

    for field, value in data.items():
        setattr(comm, field, value)
    db.add(comm)
    db.commit()
    db.refresh(comm)
    return CommunicationOut.model_validate(comm)


# PUBLIC_INTERFACE
@router.delete("/{communication_id}", status_code=200, summary="Delete communication")
def delete_communication(communication_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    """Delete a communication.

    Returns:
        dict: {"detail": "deleted"} on successful deletion.
    """
    comm = db.query(Communication).filter(Communication.id == communication_id).first()
    if not comm:
        raise HTTPException(status_code=404, detail="Communication not found")
    db.delete(comm)
    db.commit()
    return {"detail": "deleted"}
