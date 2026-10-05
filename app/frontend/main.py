import streamlit as st

from app.frontend.chat_ui import handle_user_input, render_messages
from app.frontend.session import init_session
from app.frontend.sidebar import render_sidebar

st.set_page_config(page_title="Resume Chatbot", page_icon="🤖")

init_session()
render_sidebar()
render_messages()
handle_user_input()