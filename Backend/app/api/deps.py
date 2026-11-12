"""
CLEARLY — API Dependencies
Provides dependency injection for repositories, storage, and authentication.
"""

from typing import Optional
from uuid import UUID
from fastapi import Header, HTTPException, Query, status

from app.db.repository import repository, InMemoryRepository


def get_repository() -> InMemoryRepository:
    """Dependency that returns the database repository instance."""
    return repository


def get_current_user_id(
    x_user_id: Optional[str] = Header(None, description="Optional User UUID Header")
) -> UUID:
    """
    Extracts user_id from header or defaults to Elena Pabla (Default Senior demo user).
    In production, this extracts and validates JWT session tokens.
    """
    if x_user_id:
        try:
            return UUID(x_user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de UUID inválido en header X-User-Id",
            )
    # Default to Elena Pabla (Demo senior user from Database seeds)
    return UUID("11111111-1111-1111-1111-111111111111")

