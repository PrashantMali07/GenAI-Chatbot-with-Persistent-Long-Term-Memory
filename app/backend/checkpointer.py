import aiosqlite

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.backend.memory.db import get_sqlite_connection


async def get_checkpointer() -> AsyncSqliteSaver:
    """Creates a new checkpointer connected to the SQLite DB."""
    # Note: langgraph requires the underlying aiosqlite.Connection.
    # We open a new connection for the checkpointer which langgraph manages.
    conn = await aiosqlite.connect("app/db/short-term-memory/stm.db", check_same_thread=False)
    return AsyncSqliteSaver(conn)


async def init_thread_owners_table():
    """Creates the thread ownership tracking table if it doesn't exist."""
    async with get_sqlite_connection() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS thread_owners (
                thread_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await conn.commit()


async def register_thread_owner(thread_id: str, user_id: str) -> None:
    async with get_sqlite_connection() as conn:
        await conn.execute(
            "INSERT OR IGNORE INTO thread_owners (thread_id, user_id) VALUES (?, ?)",
            (thread_id, user_id),
        )
        await conn.commit()


async def get_thread_owner(thread_id: str) -> str | None:
    """Returns the user_id that owns a thread, or None if unregistered."""
    async with get_sqlite_connection() as conn:
        async with conn.execute(
            "SELECT user_id FROM thread_owners WHERE thread_id = ?",
            (thread_id,),
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None


async def retrieve_thread_ids(user_id: str) -> list[str]:
    """Returns thread_ids belonging to a specific user, ordered by most recent."""
    async with get_sqlite_connection() as conn:
        async with conn.execute(
            "SELECT thread_id FROM thread_owners WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]


async def get_all_user_ids() -> list[str]:
    """Returns all distinct user_ids that have created at least one thread."""
    async with get_sqlite_connection() as conn:
        async with conn.execute("SELECT DISTINCT user_id FROM thread_owners ORDER BY user_id") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]


async def delete_thread(thread_id: str) -> None:
    """Deletes short-term (session) checkpoint data + ownership record."""
    checkpointer = await get_checkpointer()
    await checkpointer.adelete_thread(thread_id)
    # The checkpointer's connection should be closed after we're done since it opened a new one.
    await checkpointer.conn.close()

    async with get_sqlite_connection() as conn:
        await conn.execute("DELETE FROM thread_owners WHERE thread_id = ?", (thread_id,))
        await conn.commit()