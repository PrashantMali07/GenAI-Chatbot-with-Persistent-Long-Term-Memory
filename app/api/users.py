"""
User management endpoints.

GET /api/users   — list all known user IDs
"""

from fastapi import APIRouter

from app.backend.checkpointer import get_all_user_ids
from app.schemas import UserListResponse

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=UserListResponse)
def list_users() -> UserListResponse:
    """Return all user IDs that have at least one registered thread."""
    return UserListResponse(users=get_all_user_ids())
