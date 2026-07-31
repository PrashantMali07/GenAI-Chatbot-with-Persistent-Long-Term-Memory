"""Debug code file for future changes & individual code run"""

from app.backend.memory.postgres_raw import PostgresRawStore
from app.backend.memory.postgres_vector import PostgresVectorStore

print("Raw store:")
print(PostgresRawStore().retrieve(thread_id="chat_1", query="", k=5))

print("\nVector store:")
print(PostgresVectorStore().retrieve(thread_id="chat_1", query="What is the user's name?", k=5))