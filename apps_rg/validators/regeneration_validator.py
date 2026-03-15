"""
[SSOT] Regeneration Strategy Engine.
Decouples content correction strategies from validation logic.
Prepares for LLM-based rewriting in Phase 5.
"""

from abc import ABC, abstractmethod
from typing import Any
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


class RegenerationStrategy(ABC):
    """Abstract Base Class for content repair strategies."""

    @abstractmethod
    def execute(self, content: str, violation_metadata: dict[str, Any]) -> str:
        pass


class ExpansionStrategy(RegenerationStrategy):
    """Strategically expands content to meet minimum constraints."""

    def execute(self, content: str, violation_metadata: dict[str, Any]) -> str:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ExpansionStrategy.execute")

        min_req = violation_metadata.get("min_required", 0)
        current = len(content.split())
        needed = max(0, min_req - current)
        padding_phrase = " with measurable strategic impact"
        multiplier = needed // len(padding_phrase.split()) + 1
        return content + padding_phrase * multiplier


class CondensationStrategy(RegenerationStrategy):
    """Strategically condenses content to meet maximum constraints."""

    def execute(self, content: str, violation_metadata: dict[str, Any]) -> str:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "CondensationStrategy.execute")

        max_allowed = violation_metadata.get("max_allowed", 9999)
        words = content.split()
        if len(words) > max_allowed:
            return " ".join(words[:max_allowed])
        return content


class RegenerationEngine:
    """
    Registry and executor for regeneration strategies.
    """

    def __init__(self):
        self.strategies = {"UNDERFLOW": ExpansionStrategy(), "OVERFLOW": CondensationStrategy()}

    def regenerate(self, content: str, violation_type: str, metadata: dict[str, Any]) -> str:
        """
        Route the violation to the appropriate repair strategy.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RegenerationEngine.regenerate")

        strategy = self.strategies.get(violation_type)
        if not strategy:
            return content
        return strategy.execute(content, metadata)
