"""Reading Room Integration.

Context window management, reasoning path application, and safety guardrail evaluation.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
)

log = logging.getLogger(__name__)


@dataclass
class ReadingRoomResult:
    """Result from reading room processing."""
    final_output: str
    context_window_used: int
    reasoning_path: str
    safety_checks_passed: bool
    truncation_applied: bool
    metadata: dict[str, Any] = field(default_factory=dict)


class ReadingRoomIntegration:
    """Final stage integration for output generation.

    The ReadingRoomIntegration manages context windows, applies
    reasoning paths, and enforces safety guardrails.
    """

    def __init__(
        self,
        max_context_tokens: int = 4000,
        safety_threshold: float = 0.9,
    ):
        """Initialize the reading room integration.

        Args:
            max_context_tokens: Maximum tokens for context window
            safety_threshold: Minimum safety score threshold
        """
        self.max_context_tokens = max_context_tokens
        self.safety_threshold = safety_threshold

        log.info(f"ReadingRoomIntegration initialized (max_tokens={max_context_tokens})")

    def process(
        self,
        query: str,
        context_packet: str,
        evidence_contract: Any,
        reasoning_path: str = "direct",
    ) -> ReadingRoomResult:
        """Process final output generation.

        Args:
            query: Original query
            context_packet: Context packet from evidence
            evidence_contract: Evidence contract
            reasoning_path: Reasoning strategy

        Returns:
            ReadingRoomResult with final output
        """
        trace_id = f"reading_{hash(query) % 10000}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L1_REASONING, "ReadingRoomIntegration.process"
        )

        # Manage context window
        truncated_context, truncation_applied = self._manage_context(context_packet)

        # Evaluate safety
        safety_passed = self._evaluate_safety(query, truncated_context)

        # Generate output based on reasoning path
        output = self._generate_output(
            query,
            truncated_context,
            evidence_contract,
            reasoning_path,
        )

        result = ReadingRoomResult(
            final_output=output,
            context_window_used=len(truncated_context.split()),
            reasoning_path=reasoning_path,
            safety_checks_passed=safety_passed,
            truncation_applied=truncation_applied,
            metadata={
                "max_context_tokens": self.max_context_tokens,
                "safety_threshold": self.safety_threshold,
            },
        )

        _emit_records_telemetry_event(
            "reading_room",
            f"processed_{reasoning_path}"
        )

        log.debug(f"Reading room processed: {len(truncated_context.split())} tokens, safety={safety_passed}")
        return result

    def _manage_context(self, context_packet: str) -> tuple:
        """Manage context window size."""
        tokens = context_packet.split()

        if len(tokens) > self.max_context_tokens:
            # Truncate context
            truncated = " ".join(tokens[:self.max_context_tokens])
            return truncated, True

        return context_packet, False

    def _evaluate_safety(self, query: str, context: str) -> bool:
        """Evaluate safety guardrails."""
        # Mock safety evaluation
        # Would include: harmful content detection, PII detection, etc.

        # Simple check: query doesn't contain obvious harmful patterns
        harmful_patterns = ['hack', 'exploit', 'bypass security']

        query_lower = query.lower()
        for pattern in harmful_patterns:
            if pattern in query_lower:
                return False

        return True

    def _generate_output(
        self,
        query: str,
        context: str,
        evidence_contract: Any,
        reasoning_path: str,
    ) -> str:
        """Generate final output."""
        # Mock output generation
        # Would call LLM with appropriate prompt

        if reasoning_path == "abstain":
            return "I cannot provide an answer to this query."

        citations = getattr(evidence_contract, 'citations', [])

        output_parts = [
            "Based on the available information, here's what I found:\n",
            context[:500],  # First 500 chars of context
            f"\n\nSources: {len(citations)} documents",
        ]

        return "\n".join(output_parts)


# Global instance
_global_reading_room: ReadingRoomIntegration | None = None


def get_reading_room_integration() -> ReadingRoomIntegration:
    """Get or create the global reading room integration."""
    global _global_reading_room
    if _global_reading_room is None:
        _global_reading_room = ReadingRoomIntegration()
    return _global_reading_room
