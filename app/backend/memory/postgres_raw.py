
from langsmith import traceable

from app.backend.memory.base import BaseMemoryStore
from app.backend.memory.db import get_connection


class PostgresRawStore(BaseMemoryStore):
    @traceable(name="raw_store")
    def store(self, user_id: str, thread_id: str, summary: str) -> None:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO long_term_memory_raw (user_id, thread_id, summary)
                    VALUES (%s, %s, %s)
                    """,
                    (user_id, thread_id, summary),
                )
            conn.commit()
        finally:
            conn.close()

    @traceable(name="raw_retrieve")
    def retrieve(self, user_id: str, query: str, k: int = 5) -> list[str]:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT summary FROM long_term_memory_raw
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (user_id, k),
                )
                rows = cur.fetchall()
            return [row[0] for row in rows]
        finally:
            conn.close()