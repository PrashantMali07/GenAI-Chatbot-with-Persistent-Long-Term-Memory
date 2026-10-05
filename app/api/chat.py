"""
POST /api/chat       — buffered JSON response
POST /api/chat/stream — SSE token-streaming response

The streaming endpoint yields each LLM token as a Server-Sent Event so
the Streamlit thin client can pipe it straight into st.write_stream().
"""

import json

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, HumanMessage

from app.backend import graph
from app.schemas import ChatRequest, ChatResponse
from app.rate_limiter import limiter

router = APIRouter(prefix="/api/chat", tags=["chat"])


def _langgraph_config(req: ChatRequest) -> dict:
    return {
        "configurable": {
            "thread_id": req.thread_id,
            "user_id": req.user_id,
        }
    }


# ---------------------------------------------------------------------------
# Non-streaming endpoint — full reply returned as JSON
# ---------------------------------------------------------------------------

@router.post("", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat(request: Request, req: ChatRequest) -> ChatResponse:
    """Send a message and receive a complete reply (buffered, no streaming)."""
    full_reply = ""
    async for chunk, _ in graph.chatbot.astream(
        {"messages": [HumanMessage(content=req.message)]},
        config=_langgraph_config(req),
        stream_mode="messages",
    ):
        if isinstance(chunk, AIMessage) and chunk.content:
            full_reply += chunk.content

    return ChatResponse(reply=full_reply, user_id=req.user_id, thread_id=req.thread_id)


# ---------------------------------------------------------------------------
# Streaming endpoint — SSE token stream
# ---------------------------------------------------------------------------

@router.post("/stream")
@limiter.limit("20/minute")
async def chat_stream(request: Request, req: ChatRequest) -> StreamingResponse:
    """Send a message and receive the reply as a Server-Sent Events stream.

    Each event is a JSON object:  ``data: {"token": "...", "done": false}``
    The final event has ``"done": true`` with an empty token.

    The Streamlit client can consume this with:
        response = requests.post(url, json=payload, stream=True)
        for line in response.iter_lines():
            ...
    """

    async def _token_generator():
        async for chunk, _ in graph.chatbot.astream(
            {"messages": [HumanMessage(content=req.message)]},
            config=_langgraph_config(req),
            stream_mode="messages",
        ):
            if isinstance(chunk, AIMessage) and chunk.content:
                payload = json.dumps({"token": chunk.content, "done": False})
                yield f"data: {payload}\n\n"

        yield f"data: {json.dumps({'token': '', 'done': True})}\n\n"

    return StreamingResponse(_token_generator(), media_type="text/event-stream")
