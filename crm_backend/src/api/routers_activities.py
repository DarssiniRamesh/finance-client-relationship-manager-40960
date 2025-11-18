from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from src.api.schemas import ActivityCreate, ActivityOut, ActivityUpdate, ActivityPage
from src.api.security import get_current_user
from src.db.models import Activity, Client, User
from src.db.session import get_db

router = APIRouter(prefix="/api/v1/activities", tags=["Activities"])


def _paginate(query, page: int, page_size: int):
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return total, items


# PUBLIC_INTERFACE
@router.get("/", response_model=ActivityPage, summary="List activities")
def list_activities(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    client_id: Optional[int] = Query(None, description="Filter by client id"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ActivityPage:
    """List activities with optional filter by client."""
    q = db.query(Activity)
    if client_id:
        q = q.filter(Activity.client_id == client_id)
    total, items = _paginate(q.order_by(Activity.created_at.desc()), page, page_size)
    return ActivityPage(meta={"page": page, "page_size": page_size, "total": total}, results=[ActivityOut.model_validate(i) for i in items])


# PUBLIC_INTERFACE
@router.post("/", response_model=ActivityOut, status_code=201, summary="Create activity")
def create_activity(payload: ActivityCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ActivityOut:
    """Create an activity linked to a client."""
    # Ensure client exists
    client = db.query(Client).filter(Client.id == payload.client_id).first()
    if not client:
        raise HTTPException(status_code=400, detail="Client not found")
    activity = Activity(
        type=payload.type or "other",
        subject=payload.subject,
        due_at=payload.due_at,
        description=payload.description,
        user_id=payload.user_id,
        client_id=payload.client_id,
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return ActivityOut.model_validate(activity)


# PUBLIC_INTERFACE
@router.get("/{activity_id}", response_model=ActivityOut, summary="Get activity")
def get_activity(activity_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ActivityOut:
    """Get an activity by id."""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return ActivityOut.model_validate(activity)


# PUBLIC_INTERFACE
@router.put("/{activity_id}", response_model=ActivityOut, summary="Update activity")
def update_activity(activity_id: int, payload: ActivityUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ActivityOut:
    """Update an activity."""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # If client_id changes, validate it
    data = payload.model_dump(exclude_unset=True)
    if "client_id" in data and data["client_id"] is not None:
        client = db.query(Client).filter(Client.id == data["client_id"]).first()
        if not client:
            raise HTTPException(status_code=400, detail="Client not found")

    for field, value in data.items():
        setattr(activity, field, value)
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return ActivityOut.model_validate(activity)


# PUBLIC_INTERFACE
@router.delete("/{activity_id}", status_code=204, response_class=Response, summary="Delete activity")
def delete_activity(activity_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Response:
    """Delete an activity.

    Note: 204 No Content must not include a response body. We return None.
    """
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    db.delete(activity)
    db.commit()
    return Response(status_code=204)
