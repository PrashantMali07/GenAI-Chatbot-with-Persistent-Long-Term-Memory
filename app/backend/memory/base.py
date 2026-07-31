from abc import ABC, abstractmethod
from typing import List

class BaseMemoryStore(ABC):
    @abstractmethod
    def store(self, user_id: str, thread_id: str, summary: str) -> None:
        """Saves a summarized conversation block to the database."""
        pass

    @abstractmethod
    def retrieve(self, user_id: str, thread_id: str, query: str, k: int = 5) -> List[str]:
        """Retrieves relevant past context based on the user's current query."""
        pass