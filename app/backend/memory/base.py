from abc import ABC, abstractmethod


class BaseMemoryStore(ABC):
    @abstractmethod
    def store(self, user_id: str, thread_id: str, summary: str) -> None:
        """Saves a summarized conversation block to the database."""
        pass

    @abstractmethod
    def retrieve(self, user_id: str, query: str, k: int = 5) -> list[str]:
        """Retrieves relevant past context for the given user_id and query.
        
        Note: retrieval is scoped to user_id (not thread_id) so the agent
        can recall facts from *all* of a user's past sessions.
        """
        pass