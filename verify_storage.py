"""Debug script — manually verify Postgres raw & vector long-term memory stores."""

from app.backend.memory.postgres_raw import PostgresRawStore
from app.backend.memory.postgres_vector import PostgresVectorStore

USER_ID = "default_user"  # change as needed

print("Raw store (recency-based):")
print(PostgresRawStore().retrieve(user_id=USER_ID, query="", k=5))

print("\nVector store (semantic):")
print(PostgresVectorStore().retrieve(user_id=USER_ID, query="What is the user's name?", k=5))