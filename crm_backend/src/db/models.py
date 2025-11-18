from __future__ import annotations

from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Enum,
    func,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class TimestampMixin:
    """Reusable created_at and updated_at columns with automatic timestamps."""

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class User(Base, TimestampMixin):
    """Basic user model for ownership and audit. Auth to be implemented later."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)

    # Relationships
    clients = relationship("Client", back_populates="owner", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="owner", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan")
    communications = relationship("Communication", back_populates="user", cascade="all, delete-orphan")


class Client(Base, TimestampMixin):
    """Represents a client/contact of the finance company."""

    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    company = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    owner = relationship("User", back_populates="clients")

    activities = relationship("Activity", back_populates="client", cascade="all, delete-orphan")
    communications = relationship("Communication", back_populates="client", cascade="all, delete-orphan")


class Lead(Base, TimestampMixin):
    """Represents a sales lead associated optionally to a client."""

    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    status = Column(
        Enum("new", "contacted", "qualified", "proposal", "won", "lost", name="lead_status"),
        nullable=False,
        default="new",
        server_default="new",
    )
    value = Column(Integer, nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    owner = relationship("User", back_populates="leads")

    client_id: Optional[int] = Column(Integer, ForeignKey("clients.id", ondelete="SET NULL"), nullable=True, index=True)
    client = relationship("Client")


class Activity(Base, TimestampMixin):
    """Tracks tasks/meetings related to a client."""

    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(
        Enum("call", "meeting", "task", "email", "other", name="activity_type"),
        nullable=False,
        default="other",
        server_default="other",
    )
    subject = Column(String(255), nullable=False)
    due_at = Column(DateTime(timezone=True), nullable=True)
    description = Column(Text, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    user = relationship("User", back_populates="activities")

    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    client = relationship("Client", back_populates="activities")


class Communication(Base, TimestampMixin):
    """Records communications with a client."""

    __tablename__ = "communications"

    id = Column(Integer, primary_key=True, index=True)
    channel = Column(
        Enum("email", "phone", "sms", "in_person", "other", name="communication_channel"),
        nullable=False,
        default="other",
        server_default="other",
    )
    subject = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    user = relationship("User", back_populates="communications")

    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    client = relationship("Client", back_populates="communications")
