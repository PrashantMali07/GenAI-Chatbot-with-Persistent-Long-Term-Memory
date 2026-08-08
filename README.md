# GenAI Chatbot with Persistent Long-Term Memory

A conversational chatbot built with **LangGraph** that combines session-based short-term memory with persistent, cross-session long-term memory — enabling it to recall facts about a user across entirely separate conversations, not just within a single chat.

---

## 🧠 Overview

Most chatbots forget everything the moment a session ends. This project explores a more human-like memory architecture:

- **Short-term memory** — full conversational context within a single session, backed by SQLite via LangGraph's checkpointer.
- **Long-term memory** — durable, cross-session memory backed by PostgreSQL, populated via LLM-driven summarization and retrieved on demand by the agent itself.
- **Two retrieval strategies, compared head-to-head** — raw recency-based storage vs. pgvector embedding-based semantic search — to evaluate tradeoffs in relevance and latency.

The agent decides *for itself* when past context is needed, using a dedicated `recall_memory` tool — the same way it decides when to use a calculator or search the web.

---

## ⚙️ Architecture

```
User ↔ Streamlit UI
         │
         ▼
  LangGraph Agent (tool-calling loop)
         │
    ┌────┴────────────────────┐
    │                          │
Short-Term Memory        Tools
(SQLite checkpointer)    ├── calculator
    │                    ├── wikipedia
    │                    ├── arxiv
    │                    ├── get_url_content
    │                    ├── get_stock_price (AlphaVantage)
    │                    ├── google_search (Gemini-grounded)
    │                    └── recall_memory ──┐
    │                                        ▼
    │                          Long-Term Memory (PostgreSQL)
    │                          ├── Raw store (recency-based)
    │                          └── Vector store (pgvector, semantic)
    │                                        ▲
    └──────────── Manual "Save" trigger ─────┘
                  → Incremental summarization (OpenAI)
```

**Key design decisions:**
- Long-term memory is scoped by **`user_id`**, not `thread_id` — so memory persists across *all* of a user's sessions, not just one thread.
- Summarization is **manually triggered** (via a sidebar button) and **incremental** — each trigger only summarizes messages since the last save, using the previous summary as context, to avoid re-processing entire conversation histories repeatedly.
- Memory retrieval is **tool-based**, not automatic — the LLM calls `recall_memory` only when it judges past context is relevant, keeping routine queries fast and cheap.
- `thread_id` is injected into tools via LangChain's `InjectedToolArg`, so the LLM never has to know or guess session/user identifiers itself.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | LangGraph |
| Short-term memory | SQLite (LangGraph checkpointer) |
| Long-term memory | PostgreSQL + pgvector |
| Embeddings | OpenAI (`text-embedding-3-small`) |
| LLM providers | Groq, Ollama, OpenAI (interchangeable) |
| Search grounding | Google Gemini (`google-genai`, native Search grounding) |
| Frontend | Streamlit |
| Observability | LangSmith tracing |
| DB driver | psycopg2-binary |

---

## ✨ Features

- 💬 Multi-turn conversation with full short-term context
- 🧵 Multiple chat sessions (threads) per user, switchable from the sidebar
- 👤 Multi-user support — switch between users via dropdown, or add a new one; each user's long-term memory is fully isolated
- 🗑️ Delete individual chat sessions (short-term only — long-term memory is preserved independently)
- 💾 Manual "Save to Long-Term Memory" trigger with incremental summarization
- 🔍 Dual long-term retrieval strategies, run side-by-side for comparison (raw recency vs. vector semantic search, with latency logging)
- 🧰 Tool-using agent: calculator, Wikipedia, arXiv, URL content fetch, stock prices (AlphaVantage), Google Search (Gemini-grounded)
- 📊 Full LangSmith tracing — token usage, cost, and latency visibility across the entire pipeline

---

## 📁 Project Structure

```
app/
├── frontend/
│   ├── main.py           # Streamlit entrypoint
│   ├── session.py        # Session/thread/user state management
│   ├── sidebar.py         # Sidebar UI (users, threads, memory controls)
│   └── chat_ui.py         # Chat rendering & streaming input handling
│
├── backend/
│   ├── graph.py            # LangGraph orchestration & system prompt
│   ├── checkpointer.py     # SQLite checkpointer + thread ownership tracking
│   ├── memory/
│   │   ├── base.py            # Shared BaseMemoryStore interface
│   │   ├── postgres_raw.py    # Raw (recency-based) long-term store
│   │   ├── postgres_vector.py # pgvector (semantic) long-term store
│   │   ├── summarizer.py      # Incremental summarization logic
│   │   ├── summary_state.py   # Tracks per-user/thread summarization progress
│   │   ├── comparator.py      # Side-by-side retrieval comparison + timing
│   │   └── db.py               # Postgres connection helper
│   └── llm/
│       └── providers.py       # Groq / Ollama / OpenAI provider selection
│
├── tools/
│   ├── calculator_tool.py
│   ├── wikipedia_tool.py
│   ├── arxiv_tool.py
│   ├── url_tool.py
│   ├── stock_tool.py
│   ├── google_search_tool.py
│   └── memory_tool.py     # recall_memory — agent-invoked long-term recall
│
└── config.py               # Centralized environment/config loading

db/
└── schema.sql               # PostgreSQL + pgvector schema

run.py                        # Root entrypoint for Streamlit
requirements.txt
.env.example
```

---

## 🚀 Setup

### 1. Clone & install dependencies

```bash
git clone https://github.com/PrashantMali07/GenAI-Chatbot-with-Persistent-Long-Term-Memory.git
cd GenAI-Chatbot-with-Persistent-Long-Term-Memory
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Set up PostgreSQL + pgvector

```bash
sudo -u postgres psql
```
```sql
CREATE DATABASE resume_chatbot;
\c resume_chatbot
CREATE EXTENSION IF NOT EXISTS vector;
```
Then run the schema:
```bash
psql -U <your_user> -h localhost -d resume_chatbot -f db/schema.sql
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in your keys:
```bash
cp .env.example .env
```

Required variables include API keys for your chosen LLM provider(s), `POSTGRES_URL`, `SQLITE_DB_PATH`, and (optionally) `LANGCHAIN_API_KEY` for tracing.

### 4. Run the app

```bash
streamlit run run.py
```

---

## 🧪 Testing the memory system manually

Backend components can be exercised directly without the UI:

```python
from app.backend.memory.summarizer import summarize_and_store
from app.backend.memory.comparator import compare_retrieval

# Summarize and persist a thread's conversation
summarize_and_store(user_id="default_user", thread_id="chat_1")

# Compare raw vs. vector retrieval for a query
compare_retrieval(user_id="default_user", query="What is the user's name?", k=3)
```

---

## 📌 Status

Actively developed. 

**Current focus:** migrating the backend to an async **FastAPI** service to support concurrent access and decouple the API layer from the Streamlit frontend.

---

## 📄 License

The Unlicenced