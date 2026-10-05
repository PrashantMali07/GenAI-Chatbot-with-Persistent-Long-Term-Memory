from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat_router, memory_router, sessions_router, users_router
from app.backend.checkpointer import init_thread_owners_table


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Run startup tasks before serving requests."""
    init_thread_owners_table()
    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title="GenAI Chatbot — Long-Term Memory API",
        description=(
            "Backend service for the GenAI Chatbot with Persistent Long-Term Memory. "
            "Exposes chat, session management, and memory endpoints consumed by the Streamlit UI."
        ),
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Allow the Streamlit frontend (any origin in dev; lock down in prod)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check
    @application.get("/health", tags=["health"])
    def health():
        return {"status": "ok"}

    # Routers
    application.include_router(chat_router)
    application.include_router(sessions_router)
    application.include_router(memory_router)
    application.include_router(users_router)

    return application


app = create_app()
