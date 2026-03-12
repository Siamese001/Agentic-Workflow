from abc import ABC, abstractmethod
from agentic_core.L4_state.types.memory_item_types import MemoryItem, MemoryQuery
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class BaseVectorStore(ABC):
    """
    Interface for vector database interactions.
    All methods must be Async to support high-throughput IO.
    """

    @abstractmethod
    async def initialize(self) -> None:
        """Perform any connection handshakes or schema setups."""
        pass

    @abstractmethod
    async def upsert(self, items: list[MemoryItem]) -> bool:
        """Insert or Update memory items."""
        pass

    @abstractmethod
    async def query(self, query: MemoryQuery) -> list[MemoryItem]:
        """Retrieve nearest neighbors."""
        pass

    @abstractmethod
    async def delete(self, item_ids: list[str]) -> bool:
        """Remove items by ID."""
        pass
