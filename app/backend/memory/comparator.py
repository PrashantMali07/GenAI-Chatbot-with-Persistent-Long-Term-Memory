import time
import asyncio

from langsmith import traceable

from app.backend.memory.postgres_raw import PostgresRawStore
from app.backend.memory.postgres_vector import PostgresVectorStore


@traceable(name="compare_retrieval")
async def compare_retrieval(user_id: str, query: str, k: int = 5) -> dict:
    """
    Runs both long-term memory retrieval strategies for the same query
    and returns their results side-by-side, along with basic timing,
    for comparison/logging purposes.

    Retrieval is scoped to user_id (across all threads), matching how
    the agent's recall_memory tool works.
    """
    raw_store = PostgresRawStore()
    vector_store = PostgresVectorStore()

    # We can measure execution times by wrapping the calls
    async def fetch_raw():
        t0 = time.perf_counter()
        res = await raw_store.retrieve(user_id=user_id, query=query, k=k)
        t1 = time.perf_counter()
        return res, t1 - t0

    async def fetch_vector():
        t0 = time.perf_counter()
        res = await vector_store.retrieve(user_id=user_id, query=query, k=k)
        t1 = time.perf_counter()
        return res, t1 - t0

    # Run them concurrently
    (raw_results, raw_elapsed), (vector_results, vector_elapsed) = await asyncio.gather(
        fetch_raw(), fetch_vector()
    )

    comparison = {
        "user_id": user_id,
        "query": query,
        "raw": {
            "strategy": "recency-based (raw text, most recent k)",
            "results": raw_results,
            "elapsed_seconds": round(raw_elapsed, 4),
        },
        "vector": {
            "strategy": "semantic similarity (pgvector cosine distance)",
            "results": vector_results,
            "elapsed_seconds": round(vector_elapsed, 4),
        },
    }

    _log_comparison(comparison)
    return comparison


def _log_comparison(comparison: dict) -> None:
    print(f"\n--- Retrieval Comparison | user: {comparison['user_id']} | query: \"{comparison['query']}\" ---")
    print(f"[RAW]    ({comparison['raw']['elapsed_seconds']}s)")
    for i, r in enumerate(comparison["raw"]["results"], 1):
        print(f"  {i}. {r[:100]}{'...' if len(r) > 100 else ''}")

    print(f"[VECTOR] ({comparison['vector']['elapsed_seconds']}s)")
    for i, r in enumerate(comparison["vector"]["results"], 1):
        print(f"  {i}. {r[:100]}{'...' if len(r) > 100 else ''}")
    print("---\n")