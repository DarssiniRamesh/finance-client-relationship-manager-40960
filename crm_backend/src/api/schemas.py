from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field


# Shared pagination parameters
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="1-based page number")
    page_size: int = Field(20, ge=1, le=200, description="Items per page")
    search: Optional[str] = Field(None, description="Optional search query")


class PageMeta(BaseModel):
    page: int = Field(..., description="Current page (1-based)")
    page_size: int = Field(..., description="Page size")
    total: int = Field(..., description="Total items count")


class Page(BaseModel):
    meta: PageMeta
    # results field will be declared by concrete response models via generics at runtime


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)


class UserOut(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token TTL in seconds")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Client schemas
class ClientBase(BaseModel):
    name: str = Field(..., min_length=1)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None


class ClientCreate(ClientBase):
    owner_id: Optional[int] = Field(None, description="Owner user id")


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None
    owner_id: Optional[int] = None


class ClientOut(ClientBase):
    id: int
    owner_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClientPage(Page):
    results: List[ClientOut]


# Lead schemas
class LeadBase(BaseModel):
    title: str = Field(..., min_length=1)
    status: str = Field("new", description="new|contacted|qualified|proposal|won|lost")
    value: Optional[int] = Field(None, ge=0)
    client_id: Optional[int] = None
    owner_id: Optional[int] = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = Field(None, description="new|contacted|qualified|proposal|won|lost")
    value: Optional[int] = Field(None, ge=0)
    client_id: Optional[int] = None
    owner_id: Optional[int] = None


class LeadTransition(BaseModel):
    to_status: str = Field(..., description="Target status: new|contacted|qualified|proposal|won|lost")


class LeadOut(LeadBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeadPage(Page):
    results: List[LeadOut]


# Activity schemas
class ActivityBase(BaseModel):
    type: str = Field("other", description="call|meeting|task|email|other")
    subject: str = Field(..., min_length=1)
    due_at: Optional[datetime] = None
    description: Optional[str] = None
    user_id: Optional[int] = None
    client_id: int


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(BaseModel):
    type: Optional[str] = Field(None, description="call|meeting|task|email|other")
    subject: Optional[str] = None
    due_at: Optional[datetime] = None
    description: Optional[str] = None
    user_id: Optional[int] = None
    client_id: Optional[int] = None


class ActivityOut(ActivityBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActivityPage(Page):
    results: List[ActivityOut]


# Communication schemas
class CommunicationBase(BaseModel):
    channel: str = Field("other", description="email|phone|sms|in_person|other")
    subject: Optional[str] = None
    content: Optional[str] = None
    user_id: Optional[int] = None
    client_id: int


class CommunicationCreate(CommunicationBase):
    pass


class CommunicationUpdate(BaseModel):
    channel: Optional[str] = Field(None, description="email|phone|sms|in_person|other")
    subject: Optional[str] = None
    content: Optional[str] = None
    user_id: Optional[int] = None
    client_id: Optional[int] = None


class CommunicationOut(CommunicationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommunicationPage(Page):
    results: List[CommunicationOut]


# Metrics schema
class MetricsOut(BaseModel):
    clients: int
    leads: int
    activities: int
    communications: int
