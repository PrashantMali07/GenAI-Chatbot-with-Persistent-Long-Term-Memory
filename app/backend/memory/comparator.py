import time
from app.backend.memory.postgres_raw import PostgresRawStore
from app.backend.memory.postgres_vector import PostgresVectorStore

from langsmith import traceable

@traceable(name="compare_retrieval")
def compare_retrieval(thread_id: str, query: str, k: int = 5) -> dict:
    """
    Runs both long-term memory retrieval strategies for the same query
    and returns their results side-by-side, along with basic timing,
    for comparison/logging purposes.
    """
    raw_store = PostgresRawStore()
    vector_store = PostgresVectorStore()

    start_raw = time.perf_counter()
    raw_results = raw_store.retrieve(thread_id=thread_id, query=query, k=k)
    raw_elapsed = time.perf_counter() - start_raw

    start_vector = time.perf_counter()
    vector_results = vector_store.retrieve(thread_id=thread_id, query=query, k=k)
    vector_elapsed = time.perf_counter() - start_vector

    comparison = {
        "thread_id": thread_id,
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
    print(f"\n--- Retrieval Comparison | thread: {comparison['thread_id']} | query: \"{comparison['query']}\" ---")
    print(f"[RAW]    ({comparison['raw']['elapsed_seconds']}s)")
    for i, r in enumerate(comparison["raw"]["results"], 1):
        print(f"  {i}. {r[:100]}{'...' if len(r) > 100 else ''}")

    print(f"[VECTOR] ({comparison['vector']['elapsed_seconds']}s)")
    for i, r in enumerate(comparison["vector"]["results"], 1):
        print(f"  {i}. {r[:100]}{'...' if len(r) > 100 else ''}")
    print("---\n")