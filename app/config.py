import os
from dotenv import load_dotenv

load_dotenv()

# LLM Providers
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Tools
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")

# Databases
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "checkpoint.db")
POSTGRES_URL = os.getenv("POSTGRES_URL")  # e.g. postgresql://user:pass@host:port/dbname

# Memory
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_EMBEDDING_DIM = int(os.getenv("OPENAI_EMBEDDING_DIM", "1536"))

# For Langsmith Tracing
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "resume-chatbot")