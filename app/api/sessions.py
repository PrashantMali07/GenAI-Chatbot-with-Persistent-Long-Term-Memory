"""
Session / thread management endpoints.

GET    /api/users/{user_id}/threads           — list threads for a user
POST   /api/users/{user_id}/threads           — create new thread
DELETE /api/threads/{thread_id}               — delete a thread (STM only)
GET    /api/threads/{thread_id}/history       — load conversation history
"""

import uuid

from fastapi import APIRouter, HTTPException
from langchain_core.messages import AIMessage, HumanMessage

from app.backend.checkpointer import (
    delete_thread,
    register_thread_owner,
    retrieve_thread_ids,
)
from app.backend import graph
from app.schemas import (
    ThreadHistoryResponse,
    ThreadInfo,
    ThreadListResponse,
)

router = APIRouter(tags=["sessions"])


async def _get_thread_label(thread_id: str) -> str:
    """Return a short preview label from the first user message in the thread."""
    try:
        snapshot = await graph.chatbot.aget_state(config={"configurable": {"thread_id": thread_id}})
        messages = snapshot.values.get("messages", [])
        for msg in messages:
            if isinstance(msg, HumanMessage) and msg.content:
                words = msg.content.split()
                preview = " ".join(words[:6])
                return preview + ("..." if len(words) > 6 else "")
    except Exception:
        pass
    return "New chat"


async def _load_conversation(thread_id: str) -> list[dict]:
    """Convert LangGraph checkpoint messages into role/content dicts."""
    try:
        snapshot = await graph.chatbot.aget_state(config={"configurable": {"thread_id": thread_id}})
        raw_messages = snapshot.values.get("messages", [])
    except Exception:
        return []

    formatted = []
    for msg in raw_messages:
        if isinstance(msg, HumanMessage) and msg.content:
            formatted.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage) and msg.content:
            formatted.append({"role": "assistant", "content": msg.content})
    return formatted


# ---------------------------------------------------------------------------
# List threads
# ---------------------------------------------------------------------------

@router.get("/api/users/{user_id}/threads", response_model=ThreadListResponse)
async def list_threads(user_id: str) -> ThreadListResponse:
    """Return all threads (with preview labels) belonging to a user."""
    thread_ids = await retrieve_thread_ids(user_id)
    # Fetch labels concurrently for speed
    import asyncio
    labels = await asyncio.gather(*[_get_thread_label(tid) for tid in thread_ids])
    threads = [ThreadInfo(thread_id=tid, label=lbl) for tid, lbl in zip(thread_ids, labels)]
    return ThreadListResponse(user_id=user_id, threads=threads)


# ---------------------------------------------------------------------------
# Create thread
# ---------------------------------------------------------------------------

@router.post("/api/users/{user_id}/threads", response_model=ThreadInfo, status_code=201)
async def create_thread(user_id: str) -> ThreadInfo:
    """Create a new empty thread for the user and return its ID."""
    thread_id = str(uuid.uuid4())
    await register_thread_owner(thread_id, user_id)
    return ThreadInfo(thread_id=thread_id, label="New chat")


# ---------------------------------------------------------------------------
# Delete thread
# ---------------------------------------------------------------------------

@router.delete("/api/threads/{thread_id}", status_code=204)
async def remove_thread(thread_id: str) -> None:
    """Delete a thread's short-term memory checkpoint.
    Long-term memory (Postgres) is NOT affected — it persists independently.
    """
    try:
        await delete_thread(thread_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Thread history
# ---------------------------------------------------------------------------

@router.get("/api/threads/{thread_id}/history", response_model=ThreadHistoryResponse)
async def thread_history(thread_id: str) -> ThreadHistoryResponse:
    """Return the human-readable message history for a thread."""
    messages = await _load_conversation(thread_id)
    return ThreadHistoryResponse(thread_id=thread_id, messages=messages)
