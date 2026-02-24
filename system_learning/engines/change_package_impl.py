"""Concrete implementation of ChangePackage for testing and production use."""

from __future__ import annotations

from dataclasses import dataclass


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
    """

    source: str
    target: str
    changes: bytes
    confidence: float
    reason: tuple[str, ...]
    timestamp_utc: int

    def canonical_bytes(self) -> bytes:
        """Return deterministic canonical byte representation."""
        import json

        return json.dumps(
            {
                "source": self.source,
                "target": self.target,
                "changes": self.changes.decode("utf-8", errors="replace"),
                "confidence": self.confidence,
                "reason": list(self.reason),
                "timestamp_utc": self.timestamp_utc,
            },
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
