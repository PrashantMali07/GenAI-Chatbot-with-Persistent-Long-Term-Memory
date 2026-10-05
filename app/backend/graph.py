from typing import Annotated, TypedDict

import aiosqlite
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.backend.llm.provider import fallback_llm
from app.tools import all_tools
from app.config import SQLITE_DB_PATH

## Binding Tools
llm_with_tools = fallback_llm.bind_tools(all_tools)

## Tool node
tool_node = ToolNode(all_tools)

## -----------------> Define the graph node and state
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

SYSTEM_PROMPT = SystemMessage(content="""You are a helpful assistant with access to tools,
including a long-term memory tool (`recall_memory`) that retrieves relevant information
from the user's past conversations across sessions.

IMPORTANT: Always call `recall_memory` first whenever the user asks about themselves —
including questions like "who am I", "what's my name", "what do you know about me",
or anything referencing their own identity, preferences, or past statements — even if
this is a new conversation with no visible history. Never say you don't know who the
user is without first checking `recall_memory`.

When using information from `recall_memory` (or any tool), NEVER paste, quote, or repeat
the raw tool output back to the user. Instead, extract only the relevant fact(s) needed
to answer their question and respond in a short, natural sentence — as if you simply
remembered it yourself. For example, if the tool returns a long summary mentioning the
user's name is Prashant, just say "Your name is Prashant." — do not include the rest of
the summary or any other unrelated details from the tool output.

Use `google_search` for general questions requiring current or real-world
information not covered by other tools. Use `get_url_content` only when the
user provides a specific URL to read.

Do not use tools for general knowledge questions unrelated to the user's history.""")

async def chat_node(state: ChatState) -> ChatState:
    messages = state['messages']

    # Prepend system prompt if not already present
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SYSTEM_PROMPT] + messages

    response = await llm_with_tools.ainvoke(messages)

    return {'messages': [response]}

## -----------------> Building the graph
graph = StateGraph(ChatState)

graph.add_node('chat_node', chat_node) 
graph.add_node('tools', tool_node)

graph.add_edge(START, 'chat_node') 
graph.add_conditional_edges('chat_node', tools_condition) 
graph.add_edge('tools', 'chat_node')

# Global references
chatbot = None
_sqlite_conn = None

async def init_chatbot():
    """Initializes the async checkpointer and compiles the graph."""
    global chatbot, _sqlite_conn
    _sqlite_conn = await aiosqlite.connect(SQLITE_DB_PATH, check_same_thread=False)
    checkpointer = AsyncSqliteSaver(_sqlite_conn)
    chatbot = graph.compile(checkpointer=checkpointer)

async def close_chatbot():
    """Closes the async checkpointer connection."""
    global _sqlite_conn
    if _sqlite_conn:
        await _sqlite_conn.close()
        _sqlite_conn = None