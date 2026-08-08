import uuid
import streamlit as st
from langchain_core.messages import HumanMessage
from app.backend.graph import chatbot
from app.backend.checkpointer import (
    retrieve_thread_ids,
    register_thread_owner,
    delete_thread as backend_delete_thread,
    get_all_user_ids,
    init_thread_owners_table,
)
from langchain_core.messages import HumanMessage, AIMessage

DEFAULT_USER_ID = "default_user"


def generate_thread_id() -> str:
    return str(uuid.uuid4())


def add_threads(thread_id: str):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


def reset_chat():
    """Creates and activates a new thread for the current user."""
    thread_id = generate_thread_id()
    register_thread_owner(thread_id, st.session_state["user_id"])
    st.session_state["thread_id"] = thread_id
    add_threads(thread_id)
    st.session_state["messages"] = []


def delete_thread(thread_id: str):
    backend_delete_thread(thread_id)

    if thread_id in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].remove(thread_id)

    if st.session_state["thread_id"] == thread_id:
        st.session_state["thread_id"] = None
        st.session_state["messages"] = []


def load_conversation(thread_id: str) -> list[dict]:
    try:
        snapshot = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
        raw_messages = snapshot.values.get("messages", [])
    except Exception:
        return []

    formatted = []
    for message in raw_messages:
        if isinstance(message, HumanMessage) and message.content:
            formatted.append({"role": "user", "content": message.content})
        elif isinstance(message, AIMessage) and message.content:
            # Skipped AIMessages that only contain tool_calls with no actual text content
            formatted.append({"role": "assistant", "content": message.content})
        # ToolMessage, SystemMessage, and empty AIMessages (tool-call-only) are intentionally excluded

    return formatted


def get_thread_label(thread_id: str) -> str:
    messages = load_conversation(thread_id)
    for msg in messages:
        if msg["role"] == "user":
            words = msg["content"].split()
            preview = " ".join(words[:6])
            return preview + ("..." if len(words) > 6 else "")
    return "New chat"


def switch_user(user_id: str):
    """Switches the active user and refreshes their thread list."""
    st.session_state["user_id"] = user_id
    st.session_state["chat_threads"] = retrieve_thread_ids(user_id)
    st.session_state["thread_id"] = None
    st.session_state["messages"] = []


def init_session():
    init_thread_owners_table()

    if "user_id" not in st.session_state:
        st.session_state["user_id"] = DEFAULT_USER_ID

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    if "thread_id" not in st.session_state:
        st.session_state["thread_id"] = None

    if "chat_threads" not in st.session_state:
        st.session_state["chat_threads"] = retrieve_thread_ids(st.session_state["user_id"])