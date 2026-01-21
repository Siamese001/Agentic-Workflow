from __future__ import annotations

"""
Envelope Factory
Creates and manages data envelopes for pipeline processing.
"""
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

Logger: Any = logging.getLogger(__name__)


@dataclass
class Envelope:
    """Data Envelope for pipeline processing."""

    id: str
    data: Any
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    completed_stages: set = field(default_factory=set)

    def has_completed_stage(self, stage_name: str) -> bool:
        """Check if stage is completed."""
        return stage_name in self.completed_stages

    def mark_stage_start(self, stage_name: str) -> None:
        """Mark stage as started."""
        Logger.debug(f"Stage started: {stage_name}")

    def mark_stage_complete(self, stage_name: str) -> None:
        """Mark stage as completed."""
        self.completed_stages.add(stage_name)
        Logger.debug(f"Stage completed: {stage_name}")

    def mark_stage_skipped(self, stage_name: str, reason: str) -> None:
        """Mark stage as skipped."""
        Logger.debug(f"Stage skipped: {stage_name} - {reason}")


class EnvelopeFactory:
    """Factory for creating envelopes."""

    @staticmethod
    def create_envelope(
        data: Any, metadata: dict[str, Any] | None = None, envelope_id: str | None = None
    ) -> Envelope:
        """Create a new Envelope."""
        import uuid

        envelope_id: Any = envelope_id or str(uuid.uuid4())
        metadata: Any = metadata or {}
        Envelope: Any = Envelope(id=envelope_id, data=data, metadata=metadata)
        Logger.debug(f"Envelope created: {envelope_id}")
        return Envelope


__all__ = ["Envelope", "EnvelopeFactory"]
