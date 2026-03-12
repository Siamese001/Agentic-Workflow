"""Concrete implementation of ChangePackage for testing and production use."""
from __future__ import annotations
from dataclasses import dataclass
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

@dataclass(frozen=True, slots=True)
class ChangePackage:
    """Concrete implementation of ChangePackage protocol.

    Attributes:
        source: Source identifier for the change.
        target: Target identifier for the change.
        changes: Raw bytes representing the change.
        confidence: Confidence level (0.0 to 1.0).
        reason: Tuple of reason strings.
        timestamp_utc: UTC timestamp.
        authority_sensitivity: Authority sensitivity level (LOW/MEDIUM/HIGH).
        target_surface: Target surface identifier for mutation containment.
    """
    source: str
    target: str
    changes: bytes
    confidence: float
    reason: tuple[str, ...]
    timestamp_utc: int
    embedding_context_hash: str | None = None
    authority_sensitivity: str = 'MEDIUM'
    target_surface: str | None = None

    @property
    def reasons(self) -> tuple[str, ...]:
        """Alias for reason tuple (for API compatibility)."""
        return self.reason

    def canonical_bytes(self) -> bytes:
        """Return deterministic canonical byte representation."""
        import json
        return json.dumps({'source': self.source, 'target': self.target, 'changes': self.changes.decode('utf-8', errors='replace'), 'confidence': self.confidence, 'reason': list(self.reason), 'timestamp_utc': self.timestamp_utc, 'embedding_context_hash': self.embedding_context_hash, 'authority_sensitivity': self.authority_sensitivity, 'target_surface': self.target_surface}, separators=(',', ':'), sort_keys=True).encode('utf-8')
