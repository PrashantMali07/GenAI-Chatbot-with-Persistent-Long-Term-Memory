from app.backend.memory.db import get_pg_connection


async def get_summary_state(user_id: str, thread_id: str) -> tuple[int, str | None]:
    async with get_pg_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT last_summarized_message_count, last_summary
                FROM thread_summary_state
                WHERE user_id = %s AND thread_id = %s
                """,
                (user_id, thread_id),
            )
            row = await cur.fetchone()
        return row if row else (0, None)


async def update_summary_state(user_id: str, thread_id: str, message_count: int, summary: str) -> None:
    async with get_pg_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO thread_summary_state (user_id, thread_id, last_summarized_message_count, last_summary, updated_at)
                VALUES (%s, %s, %s, %s, now())
                ON CONFLICT (user_id, thread_id)
                DO UPDATE SET
                    last_summarized_message_count = EXCLUDED.last_summarized_message_count,
                    last_summary = EXCLUDED.last_summary,
                    updated_at = now()
                """,
                (user_id, thread_id, message_count, summary),
            )
        await conn.commit()