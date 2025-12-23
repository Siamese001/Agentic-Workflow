"""
Envelope Factory
Creates and manages data envelopes for pipeline processing.
"""
import logging
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Envelope:
    """Data envelope for pipeline processing."""
    id: str
    data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    completed_stages: set = field(default_factory=set)
    
    def has_completed_stage(self, stage_name: str) -> bool:
        """Check if stage is completed."""
        return stage_name in self.completed_stages
    
    def mark_stage_start(self, stage_name: str) -> None:
        """Mark stage as started."""
        logger.debug(f"Stage started: {stage_name}")
    
    def mark_stage_complete(self, stage_name: str) -> None:
        """Mark stage as completed."""
        self.completed_stages.add(stage_name)
        logger.debug(f"Stage completed: {stage_name}")
    
    def mark_stage_skipped(self, stage_name: str, reason: str) -> None:
        """Mark stage as skipped."""
        logger.debug(f"Stage skipped: {stage_name} - {reason}")


class EnvelopeFactory:
    """Factory for creating envelopes."""
    
    @staticmethod
    def create_envelope(
        data: Any,
        metadata: Optional[Dict[str, Any]] = None,
        envelope_id: Optional[str] = None
    ) -> Envelope:
        """Create a new envelope."""
        import uuid
        
        envelope_id = envelope_id or str(uuid.uuid4())
        metadata = metadata or {}
        
        envelope = Envelope(
            id=envelope_id,
            data=data,
            metadata=metadata
        )
        
        logger.debug(f"Envelope created: {envelope_id}")
        return envelope


__all__ = [
    "Envelope",
    "EnvelopeFactory",
]
