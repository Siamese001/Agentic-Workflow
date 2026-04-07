"""Trace ID generator with deterministic replay support.

Ensures TraceID is deterministic under replay conditions.
"""

from __future__ import annotations

import hashlib
import re
import uuid

from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    emit_determinism_digest,
    emit_replay_key,
)


class TraceIdGenerator:
    """Generates deterministic TraceIDs with replay support."""

    TRACE_ID_PATTERN = re.compile("^CC3AL1-[0-9A-F]{8}$")

    def __init__(self, replay_mode: bool = False):
        """Initialize generator.

        Args:
            replay_mode: If True, generates deterministic IDs for replay
        """
        self.replay_mode = replay_mode
        self._seed_counter = 0

    def generate_trace_id(
        self, semantic_clock: SemanticClockSnapshot, operation: str, additional_context: str | None = None,
    ) -> str:
        """Generate a deterministic TraceID.

        Args:
            semantic_clock: Current semantic clock snapshot
            operation: Operation being performed
            additional_context: Optional additional context for uniqueness

        Returns:
            TraceID matching pattern ^CC3AL1-[0-9A-F]{8}$
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L0_ROUTING, "TraceIdGenerator.generate_trace_id",
        )
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        input_parts = ["CC3AL1", str(semantic_clock.tick), operation, additional_context or ""]
        if self.replay_mode:
            input_parts.append(f"replay_{self._seed_counter}")
            self._seed_counter += 1
        input_string = "|".join(input_parts)
        hash_bytes = hashlib.sha256(input_string.encode("utf-8")).digest()
        hash_suffix = hash_bytes[:4].hex().upper()
        return f"CC3AL1-{hash_suffix}"

    def validate_trace_id(self, trace_id: str) -> bool:
        """Validate TraceID matches required pattern.

        Args:
            trace_id: TraceID to validate

        Returns:
            True if valid, False otherwise
        """
        return bool(self.TRACE_ID_PATTERN.match(trace_id))

    def is_replay_deterministic(
        self,
        trace_id1: str,
        trace_id2: str,
        semantic_clock: SemanticClockSnapshot,
        operation: str,
        additional_context: str | None = None,
    ) -> bool:
        """Check if two TraceIDs would be deterministic under same conditions.

        Args:
            trace_id1: First TraceID
            trace_id2: Second TraceID
            semantic_clock: Semantic clock snapshot
            operation: Operation being performed
            additional_context: Additional context

        Returns:
            True if IDs would be deterministic under same conditions
        """
        expected_id = self.generate_trace_id(semantic_clock, operation, additional_context)
        return trace_id1 == expected_id and trace_id2 == expected_id


_default_generator = TraceIdGenerator(replay_mode=False)


def generate_trace_id(
    semantic_clock: SemanticClockSnapshot,
    operation: str,
    additional_context: str | None = None,
    replay_mode: bool = False,
) -> str:
    """Generate a TraceID.

    Args:
        semantic_clock: Current semantic clock snapshot
        operation: Operation being performed
        additional_context: Optional additional context
        replay_mode: If True, generates deterministic ID for replay

    Returns:
        TraceID matching pattern ^CC3AL1-[0-9A-F]{8}$
    """
    if replay_mode:
        generator = TraceIdGenerator(replay_mode=True)
        return generator.generate_trace_id(semantic_clock, operation, additional_context)
    else:
        return _default_generator.generate_trace_id(semantic_clock, operation, additional_context)


def validate_trace_id(trace_id: str) -> bool:
    """Validate TraceID matches required pattern.

    Args:
        trace_id: TraceID to validate

    Returns:
        True if valid, False otherwise
    """
    _emit_applies_guardrail(str(uuid.uuid4()), "Module.validate_trace_id", "L0_ROUTING")
    return _default_generator.validate_trace_id(trace_id)
