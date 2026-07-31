from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages

from typing import TypedDict, Literal, Annotated
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage

from app.tools import all_tools
from app.backend.llm.provider import fallback_llm
from app.backend.checkpointer import get_checkpointer

## Binding Tools
llm_with_tools = fallback_llm.bind_tools(all_tools)

## Tool node
tool_node = ToolNode(all_tools)

## STM Check Pointer
check_pointer = get_checkpointer()

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

def chat_node(state: ChatState) -> ChatState:
    messages = state['messages']

    # Prepend system prompt if not already present
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SYSTEM_PROMPT] + messages

    response = llm_with_tools.invoke(messages)

    return {'messages': [response]}

## -----------------> Building the graph
graph = StateGraph(ChatState)

graph.add_node('chat_node', chat_node) 
graph.add_node('tools', tool_node)

graph.add_edge(START, 'chat_node') 
graph.add_conditional_edges('chat_node', tools_condition) 
graph.add_edge('tools', 'chat_node')

chatbot = graph.compile(checkpointer=check_pointer)

## Debug code
if __name__ == "__main__":
    CONFIG = {'configurable': {'thread_id': 'chat_3', 'user_id': 'default_user'}}
    print("\n--- To exit, type 'exit', 'quit', or 'bye' ---")
    while True:
        user_input = input("\nPlease type here: ")
        print("User message:", user_input)

        if user_input.strip().lower() in ['exit', 'quit', 'bye', 'thanks']:
            print("Goodbye!")
            break
        
        print("Assistant: ", end="", flush=True)
        for msg_chunk, metadata in chatbot.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode="messages"  # streams LLM tokens
        ):
            if isinstance(msg_chunk, AIMessage) and msg_chunk.content:
                print(msg_chunk.content, end="", flush=True)