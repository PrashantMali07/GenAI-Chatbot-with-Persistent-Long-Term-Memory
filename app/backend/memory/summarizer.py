from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langsmith import traceable

from app.backend.checkpointer import get_checkpointer
from app.backend.memory.postgres_raw import PostgresRawStore
from app.backend.memory.postgres_vector import PostgresVectorStore
from app.backend.memory.summary_state import get_summary_state, update_summary_state
from app.config import OPENAI_API_KEY

SUMMARIZER_MODEL = "gpt-4o-mini"


async def _get_thread_messages(thread_id: str) -> list:
    checkpointer = await get_checkpointer()
    config = {"configurable": {"thread_id": thread_id}}
    checkpoint_tuple = await checkpointer.aget_tuple(config)
    # Don't forget to close checkpointer conn since we created it via get_checkpointer
    await checkpointer.conn.close()
    
    if checkpoint_tuple is None:
        return []
    return checkpoint_tuple.checkpoint["channel_values"].get("messages", [])


def _format_messages(messages: list) -> str:
    lines = []
    for m in messages:
        role = getattr(m, "type", "unknown")
        content = getattr(m, "content", "")
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


@traceable(name="summarize_and_store")
async def summarize_and_store(user_id: str, thread_id: str) -> str:
    all_messages = await _get_thread_messages(thread_id)
    last_count, last_summary = await get_summary_state(user_id, thread_id)

    new_messages = all_messages[last_count:]
    if not new_messages:
        return last_summary or "No new messages to summarize."

    llm = ChatOpenAI(model=SUMMARIZER_MODEL, api_key=OPENAI_API_KEY, temperature=0)

    prompt = f"""You are maintaining a running summary of a conversation.

Previous summary:
{last_summary or "(none yet — this is the first summary)"}

New messages since the last summary:
{_format_messages(new_messages)}

Write an updated, concise summary that incorporates the new messages
into the existing summary. Keep it factual and information-dense."""

    response = await llm.ainvoke([
        SystemMessage(content="You summarize conversations concisely and factually."),
        HumanMessage(content=prompt),
    ])
    new_summary = response.content

    await update_summary_state(user_id, thread_id, len(all_messages), new_summary)
    
    # Run the two storage operations concurrently
    import asyncio
    await asyncio.gather(
        PostgresRawStore().store(user_id, thread_id, new_summary),
        PostgresVectorStore().store(user_id, thread_id, new_summary)
    )

    return new_summary