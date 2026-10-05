"""Debug code file for future changes & individual code run"""
# Debug Code for quick manual test on postgres and pgvector
from app.backend.checkpointer import get_checkpointer

cp = get_checkpointer()
print(hasattr(cp, "delete_thread"))