from __future__ import annotations

# NOT_AN_AGENT - This is a foundational CLASS, not a runtime agent
"""
L4StateBaseAgent - Consolidated Base for L4 State Agents

Layer: L4 - State
Responsibilities:
- Validation context management
- State ledger operations
- Memory persistence
- Context synchronization

MRO HARDENING:
- Inheritance order: SovereignBaseAgent (root)
- All L4 agents inherit from this base for consistent state management
"""

from dataclasses import dataclass
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent


@dataclass
class L4StateBaseAgent(SovereignBaseAgent):
    """
    Consolidated base for L4 State agents.

    L4 agents handle:
    - Validation context tracking
    - State ledger management
    - Memory persistence operations
    - Cross-agent state synchronization

    MRO: L4StateBaseAgent -> SovereignBaseAgent -> object
    """

    name: str = "L4StateBaseAgent"
    layer: str = "L4"

    def __post_init__(self) -> None:
        """Cooperative MRO initialization."""
        super().__post_init__()

    def get_state(self, key: str) -> Any:
        """
        Retrieve state by key.

        Override in subclasses for specialized state retrieval.
        """
        return None

    def set_state(self, key: str, value: Any) -> bool:
        """
        Set state by key.

        Override in subclasses for specialized state storage.
        """
        return False

    def validate_state(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        Validate state consistency.

        Override in subclasses for specialized state validation.
        """
        return {"valid": True, "errors": []}
