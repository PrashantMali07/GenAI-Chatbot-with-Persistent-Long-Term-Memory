"""
HTTP client for the FastAPI backend.

All Streamlit frontend code must go through this client — it must never
import backend modules directly (that would break the thin-client contract).

The API_BASE_URL defaults to localhost:8000 for local development.
Set the CHATBOT_API_URL environment variable to point at a remote instance.
"""

import json
import os
from collections.abc import Generator

import requests

API_BASE_URL = os.getenv("CHATBOT_API_URL", "http://localhost:8000")

_session = requests.Session()  # reuse TCP connections


class ChatbotAPIClient:
    """Thin wrapper around the FastAPI backend REST API."""

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------

    @staticmethod
    def list_users() -> list[str]:
        resp = _session.get(f"{API_BASE_URL}/api/users", timeout=10)
        resp.raise_for_status()
        return resp.json()["users"]

    # ------------------------------------------------------------------
    # Threads / Sessions
    # ------------------------------------------------------------------

    @staticmethod
    def list_threads(user_id: str) -> list[dict]:
        """Return [{"thread_id": str, "label": str}, ...]"""
        resp = _session.get(f"{API_BASE_URL}/api/users/{user_id}/threads", timeout=10)
        resp.raise_for_status()
        return resp.json()["threads"]

    @staticmethod
    def create_thread(user_id: str) -> dict:
        """Return {"thread_id": str, "label": str}"""
        resp = _session.post(f"{API_BASE_URL}/api/users/{user_id}/threads", timeout=10)
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def delete_thread(thread_id: str) -> None:
        resp = _session.delete(f"{API_BASE_URL}/api/threads/{thread_id}", timeout=10)
        resp.raise_for_status()

    @staticmethod
    def thread_history(thread_id: str) -> list[dict]:
        """Return [{"role": str, "content": str}, ...]"""
        resp = _session.get(f"{API_BASE_URL}/api/threads/{thread_id}/history", timeout=10)
        resp.raise_for_status()
        return resp.json()["messages"]

    # ------------------------------------------------------------------
    # Chat — streaming SSE
    # ------------------------------------------------------------------

    @staticmethod
    def chat_stream(user_id: str, thread_id: str, message: str) -> Generator[str, None, None]:
        """Yield AI response tokens one-by-one via SSE.

        Intended for use with st.write_stream():
            st.write_stream(ChatbotAPIClient.chat_stream(...))
        """
        payload = {
            "user_id": user_id,
            "thread_id": thread_id,
            "message": message,
            "stream": True,
        }
        with _session.post(
            f"{API_BASE_URL}/api/chat/stream",
            json=payload,
            stream=True,
            timeout=120,
        ) as resp:
            resp.raise_for_status()
            for raw_line in resp.iter_lines():
                if not raw_line:
                    continue
                line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line
                if not line.startswith("data:"):
                    continue
                data = json.loads(line[len("data:"):].strip())
                if data.get("done"):
                    break
                token = data.get("token", "")
                if token:
                    yield token

    # ------------------------------------------------------------------
    # Memory
    # ------------------------------------------------------------------

    @staticmethod
    def summarize(user_id: str, thread_id: str) -> str:
        """Trigger incremental summarization and return the summary text."""
        payload = {"user_id": user_id, "thread_id": thread_id}
        resp = _session.post(f"{API_BASE_URL}/api/memory/summarize", json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json()["summary"]

    @staticmethod
    def compare_memory(user_id: str, query: str, k: int = 5) -> dict:
        payload = {"user_id": user_id, "query": query, "k": k}
        resp = _session.post(f"{API_BASE_URL}/api/memory/compare", json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
