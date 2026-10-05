"""
Session state management for the Streamlit thin client.

All backend interactions go through ChatbotAPIClient — no direct backend
imports allowed here.
"""

import streamlit as st

from app.frontend.client import ChatbotAPIClient

DEFAULT_USER_ID = "default_user"


def init_session() -> None:
    """Initialise Streamlit session state on first run."""
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = DEFAULT_USER_ID

    if "thread_id" not in st.session_state:
        st.session_state["thread_id"] = None

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    if "chat_threads" not in st.session_state:
        _refresh_threads()


def _refresh_threads() -> None:
    """Reload the thread list from the API for the active user."""
    try:
        st.session_state["chat_threads"] = ChatbotAPIClient.list_threads(
            st.session_state["user_id"]
        )
    except Exception:
        st.session_state["chat_threads"] = []


def reset_chat() -> None:
    """Create a new thread via the API and activate it."""
    thread = ChatbotAPIClient.create_thread(st.session_state["user_id"])
    st.session_state["thread_id"] = thread["thread_id"]
    st.session_state["messages"] = []
    _refresh_threads()


def delete_thread(thread_id: str) -> None:
    """Delete a thread and clear state if it was the active one."""
    ChatbotAPIClient.delete_thread(thread_id)

    if st.session_state["thread_id"] == thread_id:
        st.session_state["thread_id"] = None
        st.session_state["messages"] = []

    _refresh_threads()


def load_conversation(thread_id: str) -> list[dict]:
    """Fetch the message history for a thread from the API."""
    try:
        return ChatbotAPIClient.thread_history(thread_id)
    except Exception:
        return []


def get_thread_label(thread: dict) -> str:
    """Return the preview label for a thread dict."""
    return thread.get("label", "New chat")


def switch_user(user_id: str) -> None:
    """Switch active user and reset all dependent state."""
    st.session_state["user_id"] = user_id
    st.session_state["thread_id"] = None
    st.session_state["messages"] = []
    _refresh_threads()