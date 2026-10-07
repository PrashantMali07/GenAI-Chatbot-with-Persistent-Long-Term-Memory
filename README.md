# GenAI Chatbot with Persistent Long-Term Memory (v4 - Full Stack React)

> **Note:** This is the `v4-frontend` branch (currently merged into `main`). It represents the final phase of this tutorial, featuring a decoupled **FastAPI** backend and a modern **React (Vite/Tailwind)** frontend with proper **JWT Authentication**.

A conversational chatbot built with **LangGraph** that combines session-based short-term memory with persistent, cross-session long-term memory — enabling it to recall facts about a user across entirely separate conversations, not just within a single chat.

---

## 🧠 Overview

Most chatbots forget everything the moment a session ends. This project explores a more human-like memory architecture:

- **Short-term memory** — full conversational context within a single session, backed by SQLite via LangGraph's checkpointer.
- **Long-term memory** — durable, cross-session memory backed by PostgreSQL, populated via LLM-driven summarization and retrieved on demand by the agent itself.
- **Authentication & Security** — Fully decoupled REST API secured by JWT tokens, allowing multi-user isolation.

The agent decides *for itself* when past context is needed, using a dedicated `recall_memory` tool — the same way it decides when to use a calculator or search the web.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite, Tailwind CSS v4, Zustand |
| Backend API | FastAPI, Uvicorn, Python 3.12 |
| Orchestration | LangGraph, LangChain |
| Short-term memory | SQLite (`aiosqlite` checkpointer) |
| Long-term memory | PostgreSQL + pgvector (`psycopg` async pool) |
| Embeddings | OpenAI (`text-embedding-3-small`) |
| Package manager | `uv` (Backend), `npm` (Frontend) |

---

## 🚀 Setup Guide

### 1. Clone & Install Backend Dependencies
We use `uv` for lightning-fast Python dependency management.
```bash
git clone https://github.com/PrashantMali07/GenAI-Chatbot-with-Persistent-Long-Term-Memory.git
cd GenAI-Chatbot-with-Persistent-Long-Term-Memory

# Install venv using uv, Python==3.12
uv venv --python 3.12

# Install dependencies using uv
uv sync
```

### 2. Set up PostgreSQL + pgvector
The backend requires a Postgres database with the `pgvector` and `pg_trgm` extensions enabled. If you've postgres locally installed, either stop the services first or use port other than `5432`, or `5433:5432` in `.yml` **(Recommended)**

**Option A: Using Docker (Recommended)**
```bash
docker compose up -d postgres
```

**Option B: Local Postgres Installation**
Ensure Postgres is running locally on port 5432, then run:
```bash
psql "postgresql://postgres:password@localhost:5432/resume_chatbot" -f app/db/schema.sql
```
*(Make sure to adjust the connection string to match your local Postgres credentials!)*

### 3. Environment Variables (`.env`)
Copy the example environment file:
```bash
cp .env.example .env
```
Open `.env` and fill in your database credentials and API keys.

### 4. Running the Application (Two Terminals Required)

**Terminal 1: Start the FastAPI Backend**
```bash
uv run fastapi dev app/server.py
```
*The backend will be available at `http://localhost:8000`*

**Terminal 2: Start the React Frontend**
```bash
cd web
npm install
npm run dev
```
*The frontend will be available at `http://localhost:5173`*

---

## 🤖 Configuring LLM Providers

The backend (`app/backend/llm/providers.py`) supports hot-swapping between multiple AI models depending on the environment variables provided in your `.env` file.

### Option 1: OpenAI (GPT-4o)
To use OpenAI's flagship models, simply add your API key to the `.env` file:
```env
OPENAI_API_KEY="sk-proj-..."
```
*By default, the application will prioritize OpenAI if the key is present.*

### Option 2: Google Gemini
To use Google Gemini (which also grants the agent native Google Search grounding capabilities), add your Google API key:
```env
GOOGLE_API_KEY="AIzaSy..."
```
*(If you want to force the application to use Gemini over OpenAI, you can comment out the `OPENAI_API_KEY` in your `.env` file, or modify `get_llm()` in `providers.py` to return the Gemini client).*

### Option 3: Ollama (Local Models)
To run the chatbot completely locally and for free, you can use Ollama.
1. Download and install [Ollama](https://ollama.com/).
2. Pull a model (e.g., Llama 3):
   ```bash
   ollama run llama3
   ```
3. Update your `.env` file to point to your local Ollama server:
   ```env
   OLLAMA_BASE_URL="http://localhost:11434"
   ```
*(You will need to update `providers.py` to specify the exact model string you downloaded, e.g., `model="llama3"`).*

---

## 📁 Project Structure

```text
├── app/
│   ├── api/              # FastAPI Routers (auth, chat, memory, sessions)
│   ├── backend/
│   │   ├── graph.py      # LangGraph orchestration & system prompt
│   │   ├── memory/       # PostgreSQL raw/vector storage logic
│   │   └── llm/          # Groq / Ollama / OpenAI / Gemini provider selection
│   ├── tools/            # Agent Tools (calculator, wikipedia, etc.)
│   ├── auth.py           # JWT Authentication & bcrypt hashing
│   └── server.py         # FastAPI root entrypoint
├── app/db/
│   └── schema.sql        # PostgreSQL + pgvector schema
├── web/                  # React Frontend (Vite)
│   ├── src/
│   │   ├── components/   # Sidebar, ChatInput
│   │   ├── pages/        # Login, Chat
│   │   └── store/        # Zustand state management
│   └── package.json
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```