from langchain_openai import OpenAIEmbeddings

from app.backend.memory.base import BaseMemoryStore
from app.backend.memory.db import get_pg_connection
from app.config import OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL


class PostgresVectorStore(BaseMemoryStore):
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=OPENAI_EMBEDDING_MODEL,
            api_key=OPENAI_API_KEY,
        )

    async def store(self, user_id: str, thread_id: str, summary: str) -> None:
        vector = await self.embeddings.aembed_query(summary)

        async with get_pg_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO long_term_memory_vector (user_id, thread_id, summary, embedding)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (user_id, thread_id, summary, str(vector)),
                )
            await conn.commit()

    async def retrieve(self, user_id: str, query: str, k: int = 5) -> list[str]:
        query_vector = await self.embeddings.aembed_query(query)

        async with get_pg_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT summary FROM long_term_memory_vector
                    WHERE user_id = %s
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                    """,
                    (user_id, str(query_vector), k),
                )
                rows = await cur.fetchall()
            return [row[0] for row in rows]