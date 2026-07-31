"""Debug code file for future changes & individual code run"""

from app.backend.checkpointer import get_checkpointer

checkpointer = get_checkpointer()
config = {"configurable": {"thread_id": "your-real-thread-id-here"}}

checkpoint_tuple = checkpointer.get_tuple(config)

if checkpoint_tuple is None:
    print("No checkpoint found for this thread_id — check the thread_id is correct.")
else:
    print("Keys in channel_values:", checkpoint_tuple.checkpoint["channel_values"].keys())
    print("Full channel_values:", checkpoint_tuple.checkpoint["channel_values"])