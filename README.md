resume-chatbot-longterm-memory/
├── app/
│   ├── __init__.py
│   ├── frontend/
│   │   ├── __init__.py
│   │   ├── main.py              # Streamlit entrypoint (thin — just wiring)
│   │   ├── session.py           # uuid gen, session_state helpers, reset_chat
│   │   ├── sidebar.py           # sidebar UI (thread list, session switcher)
│   │   └── chat_ui.py           # chat rendering, user_input handling
│   │
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── graph.py             # LangGraph graph definition & orchestration
│   │   ├── state.py             # State schema / TypedDict for the graph
│   │   ├── checkpointer.py      # SQLite/Postgres checkpointer setup
│   │   ├── memory/
│   │   │   ├── __init__.py
│   │   │   ├── short_term.py    # session-based memory logic
│   │   │   ├── long_term.py     # persistent memory (pgvector/embeddings)
│   │   │   └── summarizer.py    # trigger + logic for ST → LT transition
│   │   └── llm/
│   │       ├── __init__.py
│   │       └── providers.py     # Groq / Ollama / OpenAI provider selection
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── arxiv_tool.py
│   │   ├── wikipedia_tool.py
│   │   ├── stock_tool.py        # AlphaVantage
│   │   ├── url_tool.py          # get_url_content
│   │   └── calculator_tool.py
│   │
│   └── config.py                # API keys, model names, DB URLs (via env vars)
│
├── db/
│   ├── schema.sql                # Postgres/pgvector schema if used
│   └── migrations/                # if you add alembic later
│
├── tests/
│   ├── test_tools.py
│   ├── test_memory.py
│   └── test_graph.py
│
├── .env.example
├── .streamlit/
│   └── config.toml
├── requirements.txt
├── README.md
└── run.py                        # `streamlit run run.py` or similar entrypoint