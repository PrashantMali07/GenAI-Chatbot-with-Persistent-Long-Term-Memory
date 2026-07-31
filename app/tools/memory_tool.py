from typing import Annotated
from langchain_core.tools import tool, InjectedToolArg
from langchain_core.runnables import RunnableConfig
from app.backend.memory.postgres_vector import PostgresVectorStore


@tool
def recall_memory(
    query: str,
    config: Annotated[RunnableConfig, InjectedToolArg],
) -> str:
    """
    Retrieve relevant long-term memory from the user's past conversations,
    across all sessions. Use this when the user references something from
    a previous conversation, asks about their own past details/preferences,
    or when earlier context would help answer their current question.
    """
    user_id = config["configurable"].get("user_id", "default_user")

    store = PostgresVectorStore()
    results = store.retrieve(user_id=user_id, query=query, k=3)

    if not results:
        return "No relevant long-term memory found."
    return "\n---\n".join(results)