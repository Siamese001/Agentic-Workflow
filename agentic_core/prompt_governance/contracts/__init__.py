"""Contracts-only module for prompt governance context shapes."""

from __future__ import annotations

from .context_contracts import CitationAnchorContract, RetrievalContextContract, TelemetryEnvelopeContract
from .slot_contracts import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    SLOT_ORDER,
    AirlockViolationError,
    SlotC0,
    SlotD0,
    SlotI0,
    SlotS0,
    SlotU0,
)

__all__ = [
    "AirlockViolationError",
    "CitationAnchorContract",
    "RetrievalContextContract",
    "SLOT_ORDER",
    "SlotC0",
    "SlotD0",
    "SlotI0",
    "SlotS0",
    "SlotU0",
    "TelemetryEnvelopeContract",
]
