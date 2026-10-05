"""
Pydantic models for the FastAPI request/response boundary.
All API data shapes are defined here — keeping the API contract explicit
and separate from internal backend logic.
"""

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    thread_id: str = Field(..., description="Thread (session) identifier for short-term memory.")
    message: str = Field(..., description="The user's chat message.")
    stream: bool = Field(default=True, description="If True, response is streamed as SSE.")


class ChatResponse(BaseModel):
    """Used for non-streaming responses."""
    reply: str
    user_id: str
    thread_id: str


# ---------------------------------------------------------------------------
# Threads
# ---------------------------------------------------------------------------

class ThreadCreateRequest(BaseModel):
    pass # Currently no fields needed since user_id comes from JWT


class ThreadInfo(BaseModel):
    thread_id: str
    label: str = Field(description="Short preview derived from the first user message.")


class ThreadListResponse(BaseModel):
    user_id: str
    threads: list[ThreadInfo]


class ThreadHistoryResponse(BaseModel):
    thread_id: str
    messages: list[dict]  # [{"role": "user"|"assistant", "content": str}]


# ---------------------------------------------------------------------------
# Memory
# ---------------------------------------------------------------------------

class SummarizeRequest(BaseModel):
    thread_id: str


class SummarizeResponse(BaseModel):
    user_id: str
    thread_id: str
    summary: str


class CompareMemoryRequest(BaseModel):
    query: str
    k: int = Field(default=5, ge=1, le=20)


class CompareMemoryResponse(BaseModel):
    user_id: str
    query: str
    raw: dict
    vector: dict


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

class UserListResponse(BaseModel):
    users: list[str]
