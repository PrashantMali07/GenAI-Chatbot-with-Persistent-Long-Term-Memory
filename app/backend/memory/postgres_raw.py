from langsmith import traceable

from app.backend.memory.base import BaseMemoryStore
from app.backend.memory.db import get_pg_connection


class PostgresRawStore(BaseMemoryStore):
    @traceable(name="raw_store")
    async def store(self, user_id: str, thread_id: str, summary: str) -> None:
        async with get_pg_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO long_term_memory_raw (user_id, thread_id, summary)
                    VALUES (%s, %s, %s)
                    """,
                    (user_id, thread_id, summary),
                )
            await conn.commit()

    @traceable(name="raw_retrieve")
    async def retrieve(self, user_id: str, query: str, k: int = 5) -> list[str]:
        async with get_pg_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT summary FROM long_term_memory_raw
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (user_id, k),
                )
                rows = await cur.fetchall()
            return [row[0] for row in rows]