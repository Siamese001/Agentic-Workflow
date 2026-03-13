"""Contracts-only module: frozen dataclasses defining context shapes.

No execution logic. No pydantic. No runtime imports beyond stdlib.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalContextContract:
    """Shape contract for retrieval context metadata."""

    namespace: str
    max_k: int
    version: str


@dataclass(frozen=True)
class CitationAnchorContract:
    """Shape contract for a single citation anchor."""

    source_doc_id: str
    offset_start: int
    offset_end: int
    timestamp: str


@dataclass(frozen=True)
class TelemetryEnvelopeContract:
    """Shape contract for telemetry envelope fields."""

    hit_rate: float
    recall_estimate: float
    empty_result_signal: bool
