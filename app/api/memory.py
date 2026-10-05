"""
Long-term memory endpoints.

POST /api/memory/summarize   — summarize & persist a thread to Postgres
GET  /api/memory/compare     — compare raw vs. vector retrieval side-by-side
"""

from fastapi import APIRouter, HTTPException

from app.backend.memory.comparator import compare_retrieval
from app.backend.memory.summarizer import summarize_and_store
from app.schemas import (
    CompareMemoryRequest,
    CompareMemoryResponse,
    SummarizeRequest,
    SummarizeResponse,
)

router = APIRouter(prefix="/api/memory", tags=["memory"])


@router.post("/summarize", response_model=SummarizeResponse)
def summarize(req: SummarizeRequest) -> SummarizeResponse:
    """Incrementally summarize a thread's messages and store them in Postgres.

    Only messages since the last save are processed, so repeated calls
    are cheap — they don't reprocess the entire conversation history.
    """
    try:
        summary = summarize_and_store(user_id=req.user_id, thread_id=req.thread_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return SummarizeResponse(user_id=req.user_id, thread_id=req.thread_id, summary=summary)


@router.post("/compare", response_model=CompareMemoryResponse)
def compare(req: CompareMemoryRequest) -> CompareMemoryResponse:
    """Run both long-term retrieval strategies and return results side-by-side.

    Useful for evaluating raw (recency-based) vs. vector (semantic) recall
    quality for a given user and query.
    """
    try:
        result = compare_retrieval(user_id=req.user_id, query=req.query, k=req.k)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return CompareMemoryResponse(
        user_id=req.user_id,
        query=req.query,
        raw=result["raw"],
        vector=result["vector"],
    )
