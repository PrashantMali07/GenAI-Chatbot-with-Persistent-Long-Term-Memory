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
    user_id: str = Field(..., description="User identifier for long-term memory scoping.")
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
    user_id: str = Field(..., description="The user to create the thread for.")


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
    user_id: str
    thread_id: str


class SummarizeResponse(BaseModel):
    user_id: str
    thread_id: str
    summary: str


class CompareMemoryRequest(BaseModel):
    user_id: str
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
