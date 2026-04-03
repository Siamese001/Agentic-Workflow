"""Model Router - Stub implementation for reasoning compatibility."""
from enum import Enum
from typing import Any


class TaskType(Enum):
    """Types of tasks."""
    SIMPLE = "simple"
    COMPLEX = "complex"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"


class ModelRouter:
    """Stub model router."""

    def __init__(self):
        self._clients = {}
        self._usage = {}
        self._task_profiles = {}
        self._budget = {"daily_budget": 100.0, "spent": 0.0, "remaining": 100.0}

    def get_model_config(self, task_type: TaskType, complexity_score: int) -> dict[str, Any]:
        """Get model config for task."""
        return {"model": "default", "tier": "standard"}

    def _determine_tier(self, profile: Any, complexity_score: int) -> str:
        """Determine tier for task."""
        return "standard"

    def _select_model_for_tier(self, tier: str) -> str:
        """Select model for tier."""
        return "default"

    async def get_client(self, tier: str) -> Any:
        """Get client for tier."""
        return MockClient()

    def record_usage(self, model_name: str, input_tokens: int, output_tokens: int, cost: float) -> None:
        """Record usage."""
        self._budget["spent"] += cost
        self._budget["remaining"] -= cost

    def get_stats(self) -> dict[str, Any]:
        """Get stats."""
        return {"budget_info": self._budget}


class MockClient:
    """Mock client for testing."""

    async def generate(self, prompt: str) -> str:
        """Generate response."""
        return f"Generated: {prompt[:50]}..."


_router: ModelRouter | None = None


async def get_model_router() -> ModelRouter:
    """Get global model router."""
    global _router
    if _router is None:
        _router = ModelRouter()
    return _router


__all__ = ["ModelRouter", "TaskType", "get_model_router"]
