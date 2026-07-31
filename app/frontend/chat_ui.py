import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from app.backend.graph import chatbot


def render_messages():
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])


def handle_user_input():
    if st.session_state.get("thread_id") is None:
        st.info("Select an existing chat, or click **New Chat** to start a conversation.")
        return

    user_input = st.chat_input("Type here...")
    if not user_input:
        return

    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    config = {
        "configurable": {
            "thread_id": st.session_state["thread_id"],
            "user_id": st.session_state["user_id"],
        }
    }

    with st.chat_message("assistant"):
        def parsed_stream_message():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=config,
                stream_mode="messages",
            ):
                if isinstance(message_chunk, AIMessage) and message_chunk.content:
                    yield message_chunk.content

        ai_response = st.write_stream(parsed_stream_message())

    st.session_state["messages"].append({"role": "assistant", "content": ai_response})