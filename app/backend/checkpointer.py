import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from app.config import SQLITE_DB_PATH


def get_checkpointer():
    conn = sqlite3.connect(SQLITE_DB_PATH, check_same_thread=False)
    return SqliteSaver(conn)


def _get_raw_connection():
    return sqlite3.connect(SQLITE_DB_PATH, check_same_thread=False)


def init_thread_owners_table():
    """Creates the thread ownership tracking table if it doesn't exist."""
    conn = _get_raw_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS thread_owners (
            thread_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def register_thread_owner(thread_id: str, user_id: str) -> None:
    conn = _get_raw_connection()
    conn.execute(
        "INSERT OR IGNORE INTO thread_owners (thread_id, user_id) VALUES (?, ?)",
        (thread_id, user_id),
    )
    conn.commit()
    conn.close()


def retrieve_thread_ids(user_id: str) -> list[str]:
    """Returns thread_ids belonging to a specific user, ordered by most recent."""
    conn = _get_raw_connection()
    rows = conn.execute(
        "SELECT thread_id FROM thread_owners WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return [row[0] for row in rows]


def get_all_user_ids() -> list[str]:
    """Returns all distinct user_ids that have created at least one thread."""
    conn = _get_raw_connection()
    rows = conn.execute("SELECT DISTINCT user_id FROM thread_owners ORDER BY user_id").fetchall()
    conn.close()
    return [row[0] for row in rows]


def delete_thread(thread_id: str) -> None:
    """Deletes short-term (session) checkpoint data + ownership record."""
    checkpointer = get_checkpointer()
    checkpointer.delete_thread(thread_id)

    conn = _get_raw_connection()
    conn.execute("DELETE FROM thread_owners WHERE thread_id = ?", (thread_id,))
    conn.commit()
    conn.close()