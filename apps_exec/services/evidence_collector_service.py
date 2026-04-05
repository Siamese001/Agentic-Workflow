"""
Evidence Collector Service — apps_exec

Stub service for evidence collection.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import _emit_records_telemetry_event

_log = logging.getLogger(__name__)


class EvidenceCollectorService:
    """Stub service for evidence collection."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        _emit_records_telemetry_event("p4", "evidence_collector", "init")

    def collect_evidence(self, claim: str) -> list[dict[str, Any]]:
        """Collect evidence for a claim."""
        return []
