"""Contracts-only module for prompt governance context shapes."""

from __future__ import annotations

from .context_contracts import CitationAnchorContract, RetrievalContextContract, TelemetryEnvelopeContract
from .slot_contracts import (
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
