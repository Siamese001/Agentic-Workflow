# Tooling Interface and Registry
# Strategy: Standardized interface for agent capabilities

from abc import ABC, abstractmethod
from collections.abc import Callable

from pydantic import BaseModel, Field


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class BaseTool(BaseModel, ABC):
    """
    Abstract base class for all executable tools.
    """

    name: str = Field(..., description="Unique identifier for the tool")
    description: str = Field(..., description="Natural language description for the LLM")

    # Allow arbitrary types for internal logic (like API clients)
    class Config:
        arbitrary_types_allowed = True

    @abstractmethod
    async def run(self, **kwargs) -> str:
        """
        Execute the tool logic. Returns a string observation.
        """
        pass


class FunctionalTool(BaseTool):
    """
    Wrapper to turn a Python function into a Tool.
    """

    func: Callable

    async def run(self, **kwargs) -> str:
        try:
            # Handle both async and sync functions if needed,
            # for now assuming sync func wrapped in async logic or simple return
            return str(self.func(**kwargs))
        # guardian: allow-silent-swallow
        except Exception as e:
            return f"Error executing {self.name}: {str(e)}"


class ToolRegistry:
    """
    Manager for the agent's available toolkit.
    """

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        if tool.name in self._tools:
            raise ValueError(f"Tool {tool.name} already registered")
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def list_tools(self) -> str:
        return "\n".join([f"- {t.name}: {t.description}" for t in self._tools.values()])
