from langchain_openai import OpenAIEmbeddings

from app.backend.memory.base import BaseMemoryStore
from app.backend.memory.db import get_connection
from app.config import OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL


class PostgresVectorStore(BaseMemoryStore):
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=OPENAI_EMBEDDING_MODEL,
            api_key=OPENAI_API_KEY,
        )

    def store(self, user_id: str, thread_id: str, summary: str) -> None:
        vector = self.embeddings.embed_query(summary)

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO long_term_memory_vector (user_id, thread_id, summary, embedding)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (user_id, thread_id, summary, vector),
                )
            conn.commit()
        finally:
            conn.close()

    def retrieve(self, user_id: str, query: str, k: int = 5) -> list[str]:
        query_vector = self.embeddings.embed_query(query)

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT summary FROM long_term_memory_vector
                    WHERE user_id = %s
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                    """,
                    (user_id, query_vector, k),
                )
                rows = cur.fetchall()
            return [row[0] for row in rows]
        finally:
            conn.close()