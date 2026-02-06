from __future__ import annotations

# NOT_AN_AGENT - This is a foundational CLASS, not a runtime agent
"""
L1CognitionBaseAgent - Consolidated Base for L1 Cognition Agents

Layer: L1 - Cognition
Responsibilities:
- Thought engine operations
- Intent analysis
- Memory management
- Meta-learning coordination

MRO HARDENING:
- Inheritance order: SovereignBaseAgent (root)
- All L1 agents inherit from this base for consistent cognition capabilities
"""

from dataclasses import dataclass
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent


@dataclass
class L1CognitionBaseAgent(SovereignBaseAgent):
    """
    Consolidated base for L1 Cognition agents.

    L1 agents handle:
    - Thought engine operations
    - Intent analysis and classification
    - Memory retrieval and storage
    - Meta-learning pattern recognition

    MRO: L1CognitionBaseAgent -> SovereignBaseAgent -> object
    """

    name: str = "L1CognitionBaseAgent"
    layer: str = "L1"

    def __post_init__(self) -> None:
        """Cooperative MRO initialization."""
        super().__post_init__()

    def analyze_intent(self, input_text: str) -> dict[str, Any]:
        """
        Analyze user intent from input text.

        Override in subclasses for specialized intent analysis.
        """
        return {"intent": "unknown", "confidence": 0.0, "raw_input": input_text}

    def retrieve_context(self, query: str) -> list[dict[str, Any]]:
        """
        Retrieve relevant context from memory.

        Override in subclasses for specialized memory retrieval.
        """
        return []
