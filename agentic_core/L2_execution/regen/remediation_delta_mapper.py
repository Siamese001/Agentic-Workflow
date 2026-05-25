"""Protocol for app-owned delta line generation (ADR-085)."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class RemediationDeltaMapper(Protocol):
    """Apps implement: map judge/gate feedback to bounded delta lines only."""

    def map_delta_lines(self) -> tuple[str, ...]:
        """Return non-empty delta lines; no full prompt rewrite."""
