"""
Unit tests for the memory store layer.

Tests use InMemoryMemoryStore — an in-memory stub that implements
BaseMemoryStore — so no PostgreSQL connection is required.
"""

import pytest

from app.backend.memory.base import BaseMemoryStore

# ---------------------------------------------------------------------------
# In-memory stub — a real implementation against the interface
# ---------------------------------------------------------------------------

class InMemoryMemoryStore(BaseMemoryStore):
    """Simple list-backed store for unit testing."""

    def __init__(self):
        self._records: list[dict] = []

    def store(self, user_id: str, thread_id: str, summary: str) -> None:
        self._records.append({"user_id": user_id, "thread_id": thread_id, "summary": summary})

    def retrieve(self, user_id: str, query: str, k: int = 5) -> list[str]:
        return [
            r["summary"]
            for r in self._records
            if r["user_id"] == user_id
        ][-k:]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestInMemoryStore:

    def test_store_and_retrieve(self):
        store = InMemoryMemoryStore()
        store.store("alice", "t1", "Alice likes pizza")
        results = store.retrieve("alice", "pizza")
        assert results == ["Alice likes pizza"]

    def test_retrieval_is_user_scoped(self):
        store = InMemoryMemoryStore()
        store.store("alice", "t1", "Alice likes pizza")
        store.store("bob", "t2", "Bob likes tacos")

        alice_results = store.retrieve("alice", "food")
        bob_results = store.retrieve("bob", "food")

        assert all("pizza" in r for r in alice_results)
        assert all("tacos" in r for r in bob_results)
        assert not any("tacos" in r for r in alice_results)
        assert not any("pizza" in r for r in bob_results)

    def test_retrieve_empty_returns_empty_list(self):
        store = InMemoryMemoryStore()
        assert store.retrieve("nobody", "anything") == []

    def test_k_limits_results(self):
        store = InMemoryMemoryStore()
        for i in range(10):
            store.store("alice", "t1", f"Summary {i}")
        results = store.retrieve("alice", "summary", k=3)
        assert len(results) == 3

    def test_multiple_threads_same_user(self):
        store = InMemoryMemoryStore()
        store.store("alice", "t1", "Thread 1 memory")
        store.store("alice", "t2", "Thread 2 memory")
        results = store.retrieve("alice", "thread")
        # Both threads' memories should be retrievable for the same user
        assert len(results) == 2

    def test_interface_is_abstract(self):
        """BaseMemoryStore cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseMemoryStore()
