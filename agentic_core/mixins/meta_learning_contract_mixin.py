"""
agentic_core/base_agents/base_meta_learner.py

[PHASE 25] BaseMetaLearner - Abstract Base Class for Meta-Learning.
ARCHITECTURAL CONTRACT: Enforces consistency across L0-L6.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class BaseMetaLearner(ABC):
    """
    Abstract Base Class enforcing the Meta-Learning contract.

    All agents inheriting from this MUST implement:
    1. recall_experience() - Query the Hive Mind
    2. learn_experience() - Teach the Hive Mind
    3. recall_or_execute() - The Golden Path pattern
    """

    @property
    @abstractmethod
    def _namespace(self) -> str:
        """
        Get the namespace for this agent (DNA segregation).
        MUST be unique per agent type to prevent memory collisions.
        """
        pass

    @abstractmethod
    def recall_experience(self, context: str) -> dict[str, Any] | None:
        """Consult the Hive Mind for a solution to the current context."""
        pass

    @abstractmethod
    async def learn_experience(self, context: str, result: dict[str, Any]) -> None:
        """
        Teach the Hive Mind (Async/Fire-and-Forget).
        MUST validate serialization and complete in <50ms on main thread.
        Must be async method for proper awaitable support.
        """
        pass

    @abstractmethod
    def recall_or_execute(
        self,
        context: str,
        execution_fn: Callable[[], Any],
    ) -> Any:
        """The Golden Path: Check memory first, execute only if necessary."""
        pass
