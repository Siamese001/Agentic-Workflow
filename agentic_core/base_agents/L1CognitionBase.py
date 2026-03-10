from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# NOT_AN_AGENT - This is a foundational CLASS, not a runtime agent
"""
L1CognitionBase - Consolidated Base for L1 Cognition Agents

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
class L1CognitionBase(SovereignBaseAgent):
    """
    Consolidated base for L1 Cognition agents.

    L1 agents handle:
    - Thought engine operations
    - Intent analysis and classification
    - Memory retrieval and storage
    - Meta-learning pattern recognition

    MRO: L1CognitionBase -> SovereignBaseAgent -> object
    """

    name: str = "L1CognitionBase"
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
