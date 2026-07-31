import streamlit as st
from app.frontend.session import (
    reset_chat, load_conversation, delete_thread, get_thread_label, switch_user
)
from app.backend.checkpointer import get_all_user_ids
from app.backend.memory.summarizer import summarize_and_store


def render_sidebar():
    st.sidebar.title("Chatbot Controls")

    # ---------------- User selector ----------------
    st.sidebar.subheader("User")
    existing_users = get_all_user_ids()
    if st.session_state["user_id"] not in existing_users:
        existing_users.append(st.session_state["user_id"])

    options = existing_users + ["➕ Add new user..."]
    current_index = options.index(st.session_state["user_id"])

    selected = st.sidebar.selectbox("Active user", options, index=current_index, key="user_selector")

    if selected == "➕ Add new user...":
        new_user = st.sidebar.text_input("New user ID", key="new_user_input")
        if st.sidebar.button("Create user") and new_user.strip():
            switch_user(new_user.strip())
            st.rerun()
    elif selected != st.session_state["user_id"]:
        switch_user(selected)
        st.rerun()

    st.sidebar.divider()

    # ---------------- Chat controls ----------------
    if st.sidebar.button("New Chat"):
        reset_chat()

    if st.session_state.get("thread_id") and st.sidebar.button("💾 Save to Long-Term Memory"):
        with st.spinner("Summarizing and saving..."):
            summary = summarize_and_store(
                user_id=st.session_state["user_id"],
                thread_id=st.session_state["thread_id"],
            )
        st.sidebar.success("Saved!")
        st.sidebar.caption(summary)

    col_header, col_info = st.sidebar.columns([5, 1])
    with col_header:
        st.subheader("Recent Chats")
    with col_info:
        st.markdown(
            "ℹ️",
            help="Deleting a chat removes its short-term session history only. "
                 "Long-term memory is stored separately — press 💾 Save to Long-Term "
                 "Memory before deleting if you want this conversation remembered."
        )

    if not st.session_state["chat_threads"]:
        st.sidebar.caption("No chats yet — click **New Chat** to start.")

    for thread_id in st.session_state["chat_threads"]:
        label = get_thread_label(thread_id)
        col1, col2 = st.sidebar.columns([4, 1])

        with col1:
            if st.button(label, key=f"select_{thread_id}"):
                st.session_state["thread_id"] = thread_id
                st.session_state["messages"] = load_conversation(thread_id)

        with col2:
            if st.button("🗑️", key=f"delete_{thread_id}"):
                delete_thread(thread_id)
                st.rerun()