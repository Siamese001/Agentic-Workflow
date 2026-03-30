"""Envelope types - Stub implementation for test compatibility."""
from dataclasses import dataclass
from typing import Any, Dict, Optional
from enum import Enum


class EnvelopeStatus(Enum):
    """Envelope status."""
    PENDING = "pending"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    FAILED = "failed"


@dataclass
class Envelope:
    """Message envelope."""
    message_id: str
    payload: Dict[str, Any]
    status: EnvelopeStatus = EnvelopeStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    error_info: Optional[str] = None
    
    def mark_delivered(self) -> None:
        """Mark envelope as delivered."""
        self.status = EnvelopeStatus.DELIVERED
    
    def mark_failed(self, error: str) -> None:
        """Mark envelope as failed."""
        self.status = EnvelopeStatus.FAILED
        self.error_info = error


@dataclass
class SignalEnvelope:
    """Signal envelope for messaging."""
    signal_id: str
    signal_type: str
    payload: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


__all__ = ["Envelope", "EnvelopeStatus", "SignalEnvelope"]
