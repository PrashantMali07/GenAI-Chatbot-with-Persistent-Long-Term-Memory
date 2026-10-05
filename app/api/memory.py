"""
Long-term memory endpoints.

POST /api/memory/summarize   — summarize & persist a thread to Postgres
GET  /api/memory/compare     — compare raw vs. vector retrieval side-by-side
"""

from fastapi import APIRouter, HTTPException, Depends

from app.backend.memory.comparator import compare_retrieval
from app.backend.memory.summarizer import summarize_and_store
from app.schemas import (
    CompareMemoryRequest,
    CompareMemoryResponse,
    SummarizeRequest,
    SummarizeResponse,
)
from app.auth import get_current_user

router = APIRouter(prefix="/api/memory", tags=["memory"])


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(req: SummarizeRequest, user_id: str = Depends(get_current_user)) -> SummarizeResponse:
    """Incrementally summarize a thread's messages and store them in Postgres.

    Only messages since the last save are processed, so repeated calls
    are cheap — they don't reprocess the entire conversation history.
    """
    try:
        summary = await summarize_and_store(user_id=user_id, thread_id=req.thread_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return SummarizeResponse(user_id=user_id, thread_id=req.thread_id, summary=summary)


@router.post("/compare", response_model=CompareMemoryResponse)
async def compare(req: CompareMemoryRequest, user_id: str = Depends(get_current_user)) -> CompareMemoryResponse:
    """Run both long-term retrieval strategies and return results side-by-side.

    Useful for evaluating raw (recency-based) vs. vector (semantic) recall
    quality for a given user and query.
    """
    try:
        result = await compare_retrieval(user_id=user_id, query=req.query, k=req.k)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return CompareMemoryResponse(
        user_id=user_id,
        query=req.query,
        raw=result["raw"],
        vector=result["vector"],
    )
