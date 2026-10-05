import aiosqlite
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from psycopg_pool import AsyncConnectionPool
from psycopg import AsyncConnection

from app.config import POSTGRES_URL, SQLITE_DB_PATH

# Global connection pool for Postgres
_pg_pool: AsyncConnectionPool | None = None

async def init_pg_pool():
    global _pg_pool
    if _pg_pool is None:
        _pg_pool = AsyncConnectionPool(
            conninfo=POSTGRES_URL,
            min_size=1,
            max_size=10,
            timeout=30.0,
        )
        await _pg_pool.open()

async def close_pg_pool():
    global _pg_pool
    if _pg_pool is not None:
        await _pg_pool.close()
        _pg_pool = None

@asynccontextmanager
async def get_pg_connection() -> AsyncGenerator[AsyncConnection, None]:
    """Yields a managed connection from the Postgres pool."""
    if _pg_pool is None:
        raise RuntimeError("Postgres pool is not initialized. Call init_pg_pool() on startup.")
    
    async with _pg_pool.connection() as conn:
        yield conn

@asynccontextmanager
async def get_sqlite_connection() -> AsyncGenerator[aiosqlite.Connection, None]:
    """Yields a raw aiosqlite connection for thread tracking."""
    async with aiosqlite.connect(SQLITE_DB_PATH, check_same_thread=False) as conn:
        yield conn