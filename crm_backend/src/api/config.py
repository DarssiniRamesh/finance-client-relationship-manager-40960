from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List

# PUBLIC_INTERFACE
def get_bool_env(name: str, default: bool = False) -> bool:
    """Return a boolean from environment variable safely."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """Application configuration loaded from environment variables."""

    # Database configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./crm.db")

    # Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "CHANGE_ME_IN_PRODUCTION")

    # CORS
    CORS_ALLOW_ORIGINS: List[str] = tuple(
        origin.strip()
        for origin in os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")
        if origin.strip()
    )
    CORS_ALLOW_CREDENTIALS: bool = get_bool_env("CORS_ALLOW_CREDENTIALS", True)
    CORS_ALLOW_METHODS: List[str] = tuple(
        method.strip()
        for method in os.getenv("CORS_ALLOW_METHODS", "*").split(",")
        if method.strip()
    )
    CORS_ALLOW_HEADERS: List[str] = tuple(
        header.strip()
        for header in os.getenv("CORS_ALLOW_HEADERS", "*").split(",")
        if header.strip()
    )


# PUBLIC_INTERFACE
def get_settings() -> Settings:
    """Return cached Settings instance."""
    # Simple module-level memoization without global mutation.
    return Settings()
