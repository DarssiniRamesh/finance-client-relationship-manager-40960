from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from src.api.schemas import ClientCreate, ClientOut, ClientUpdate, ClientPage
from src.api.security import get_current_user
from src.db.models import Client, User
from src.db.session import get_db

router = APIRouter(prefix="/api/v1/clients", tags=["Clients"])


def _paginate(query, page: int, page_size: int):
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return total, items


# PUBLIC_INTERFACE
@router.get("/", response_model=ClientPage, summary="List clients", description="List clients with optional search and pagination.")
def list_clients(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    search: Optional[str] = Query(None, description="Search by name/email/company"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ClientPage:
    """List clients with pagination and simple search."""
    q = db.query(Client)
    if search:
        like = f"%{search.lower()}%"
        q = q.filter(
            or_(
                func.lower(Client.name).like(like),
                func.lower(Client.email).like(like),
                func.lower(Client.company).like(like),
            )
        )
    total, items = _paginate(q.order_by(Client.created_at.desc()), page, page_size)
    return ClientPage(meta={"page": page, "page_size": page_size, "total": total}, results=[ClientOut.model_validate(i) for i in items])


# PUBLIC_INTERFACE
@router.post("/", response_model=ClientOut, status_code=201, summary="Create client")
def create_client(payload: ClientCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ClientOut:
    """Create a client."""
    client = Client(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        company=payload.company,
        notes=payload.notes,
        owner_id=payload.owner_id,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return ClientOut.model_validate(client)


# PUBLIC_INTERFACE
@router.get("/{client_id}", response_model=ClientOut, summary="Get client by id")
def get_client(client_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ClientOut:
    """Get a single client by id."""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return ClientOut.model_validate(client)


# PUBLIC_INTERFACE
@router.put("/{client_id}", response_model=ClientOut, summary="Update client")
def update_client(
    client_id: int, payload: ClientUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> ClientOut:
    """Update a client."""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(client, field, value)
    db.add(client)
    db.commit()
    db.refresh(client)
    return ClientOut.model_validate(client)


# PUBLIC_INTERFACE
@router.delete("/{client_id}", status_code=204, response_class=Response, summary="Delete client")
def delete_client(client_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Response:
    """Delete a client by id.

    FastAPI requires that HTTP 204 responses have no response body and no response model.
    This endpoint intentionally returns None to comply with RFC 7231 and FastAPI validation.
    """
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(client)
    db.commit()
    # Explicitly return an empty Response to avoid any response body for 204 No Content.
    return Response(status_code=204)
