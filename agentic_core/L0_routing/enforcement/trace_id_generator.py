"""Trace ID generator with deterministic replay support.

Ensures TraceID is deterministic under replay conditions.
"""

from __future__ import annotations

import hashlib
import re

from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class TraceIdGenerator:
    """Generates deterministic TraceIDs with replay support."""

    # TraceID regex: ^CC3AL1-[0-9A-F]{8}$ (REQ-182)
    TRACE_ID_PATTERN = re.compile(r"^CC3AL1-[0-9A-F]{8}$")

    def __init__(self, replay_mode: bool = False):
        """Initialize generator.

        Args:
            replay_mode: If True, generates deterministic IDs for replay
        """
        self.replay_mode = replay_mode
        self._seed_counter = 0

    def generate_trace_id(
        self, semantic_clock: SemanticClockSnapshot, operation: str, additional_context: str | None = None
    ) -> str:
        """Generate a deterministic TraceID.

        Args:
            semantic_clock: Current semantic clock snapshot
            operation: Operation being performed
            additional_context: Optional additional context for uniqueness

        Returns:
            TraceID matching pattern ^CC3AL1-[0-9A-F]{8}$
        """
        # Build deterministic input
        input_parts = [
            "CC3AL1",
            str(semantic_clock.tick),
            operation,
            additional_context or "",
        ]

        if self.replay_mode:
            # In replay mode, use deterministic counter
            input_parts.append(f"replay_{self._seed_counter}")
            self._seed_counter += 1

        # Create deterministic hash
        input_string = "|".join(input_parts)
        hash_bytes = hashlib.sha256(input_string.encode("utf-8")).digest()

        # Take first 4 bytes (8 hex chars) for the ID
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
        # Generate expected deterministic ID
        expected_id = self.generate_trace_id(semantic_clock, operation, additional_context)

        # Both should match expected ID in replay mode
        return trace_id1 == expected_id and trace_id2 == expected_id


# Global instance for non-replay usage
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
    return _default_generator.validate_trace_id(trace_id)
