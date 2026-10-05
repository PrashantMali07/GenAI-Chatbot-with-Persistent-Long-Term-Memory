"""
Integration tests for the FastAPI endpoints using TestClient.

These tests exercise the full API routing layer including Pydantic validation.
The LangGraph chatbot and Postgres calls are mocked so no external services
are required.
"""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.server import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

@patch("app.api.users.get_all_user_ids", return_value=["alice", "bob"])
def test_list_users(mock_fn):
    resp = client.get("/api/users")
    assert resp.status_code == 200
    assert set(resp.json()["users"]) == {"alice", "bob"}


# ---------------------------------------------------------------------------
# Threads
# ---------------------------------------------------------------------------

@patch("app.api.sessions.retrieve_thread_ids", return_value=["t1", "t2"])
@patch("app.api.sessions.chatbot")
def test_list_threads(mock_chatbot, mock_retrieve):
    # Mock get_state to return an empty snapshot
    mock_chatbot.get_state.return_value = MagicMock(values={"messages": []})
    resp = client.get("/api/users/alice/threads")
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == "alice"
    assert len(data["threads"]) == 2


@patch("app.api.sessions.register_thread_owner")
def test_create_thread(mock_register):
    resp = client.post("/api/users/alice/threads")
    assert resp.status_code == 201
    data = resp.json()
    assert "thread_id" in data
    assert data["label"] == "New chat"
    mock_register.assert_called_once()


@patch("app.api.sessions.delete_thread")
def test_delete_thread(mock_delete):
    resp = client.delete("/api/threads/t1")
    assert resp.status_code == 204
    mock_delete.assert_called_once_with("t1")


@patch("app.api.sessions.chatbot")
def test_thread_history(mock_chatbot):
    from langchain_core.messages import AIMessage, HumanMessage
    mock_chatbot.get_state.return_value = MagicMock(
        values={"messages": [
            HumanMessage(content="Hello"),
            AIMessage(content="Hi there!"),
        ]}
    )
    resp = client.get("/api/threads/t1/history")
    assert resp.status_code == 200
    messages = resp.json()["messages"]
    assert messages[0] == {"role": "user", "content": "Hello"}
    assert messages[1] == {"role": "assistant", "content": "Hi there!"}


# ---------------------------------------------------------------------------
# Memory
# ---------------------------------------------------------------------------

@patch("app.api.memory.summarize_and_store", return_value="Alice is a developer.")
def test_summarize(mock_fn):
    resp = client.post("/api/memory/summarize", json={"user_id": "alice", "thread_id": "t1"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["summary"] == "Alice is a developer."
    assert data["user_id"] == "alice"


@patch("app.api.memory.compare_retrieval", return_value={
    "user_id": "alice",
    "query": "name",
    "raw": {"strategy": "recency", "results": ["Alice is a developer."], "elapsed_seconds": 0.001},
    "vector": {"strategy": "semantic", "results": ["Alice is a developer."], "elapsed_seconds": 0.005},
})
def test_compare_memory(mock_fn):
    resp = client.post("/api/memory/compare", json={"user_id": "alice", "query": "name", "k": 3})
    assert resp.status_code == 200
    data = resp.json()
    assert "raw" in data
    assert "vector" in data
    assert data["query"] == "name"


# ---------------------------------------------------------------------------
# Pydantic validation
# ---------------------------------------------------------------------------

def test_chat_request_missing_fields():
    """POST /api/chat without required fields should return 422."""
    resp = client.post("/api/chat", json={"message": "hi"})
    assert resp.status_code == 422


def test_compare_memory_k_out_of_range():
    """k=0 should fail validation (ge=1)."""
    resp = client.post("/api/memory/compare", json={"user_id": "alice", "query": "x", "k": 0})
    assert resp.status_code == 422
