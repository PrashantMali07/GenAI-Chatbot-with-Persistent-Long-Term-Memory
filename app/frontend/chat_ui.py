"""
Chat UI — renders message history and handles user input via streaming.

All LLM calls go through ChatbotAPIClient.chat_stream() (SSE) so this
module has zero backend imports.
"""

import streamlit as st

from app.frontend.client import ChatbotAPIClient


def render_messages() -> None:
    """Render the conversation history stored in session state."""
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])


def handle_user_input() -> None:
    """Handle the chat input box and stream the assistant reply."""
    if st.session_state.get("thread_id") is None:
        st.info("Select an existing chat, or click **New Chat** to start a conversation.")
        return

    user_input = st.chat_input("Type here...")
    if not user_input:
        return

    # Append and render the user message immediately
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Stream the assistant reply from the FastAPI SSE endpoint
    with st.chat_message("assistant"):
        try:
            ai_response = st.write_stream(
                ChatbotAPIClient.chat_stream(
                    user_id=st.session_state["user_id"],
                    thread_id=st.session_state["thread_id"],
                    message=user_input,
                )
            )
        except Exception as exc:
            ai_response = f"⚠️ Error contacting backend: {exc}"
            st.error(ai_response)

    st.session_state["messages"].append({"role": "assistant", "content": ai_response})