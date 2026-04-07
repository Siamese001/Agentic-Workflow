"""
Requirement Parser Service — apps_rfp

Parses and extracts requirements from RFP documents.
Aligned with apps_lic service pattern with lifecycle trace integration.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
    _emit_routes_to_capability,
    _emit_snapshots_state,
    _emit_validates_capability,
    emit_determinism_digest,
    emit_replay_key,
)

_log = logging.getLogger(__name__)


class RequirementParserService:
    """Service for parsing and extracting RFP requirements."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize the requirement parser service."""
        self.config = config or {}
        self._parsed_requirements: list[dict[str, Any]] = []
        self._requirement_patterns = [
            r"(?i)must\s+(.+)",
            r"(?i)shall\s+(.+)",
            r"(?i)required[;: ]\s*(.+)",
            r"(?i)mandatory[;: ]\s*(.+)",
        ]

        # Lifecycle trace emission
        emit_replay_key("req_parser", "init")
        emit_determinism_digest("req_parser", "init")
        _emit_applies_guardrail("p0", "req_parser", "service_init")
        _emit_snapshots_state("p0", "req_parser", "service_state")

    def parse_document(
        self,
        document_content: str,
        document_type: str = "rfp",
    ) -> list[dict[str, Any]]:
        """Parse requirements from a document.

        Args:
            document_content: Raw document text
            document_type: Type of document (rfp, proposal, etc.)

        Returns:
            List of parsed requirements
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "RequirementParserService.parse_document",
        )
        _emit_routes_to_capability("p2", "req_parser", "document_parsing")
        _emit_validates_capability("p2", "req_parser", "content_analysis")
        _emit_records_telemetry_event("p4", "req_parser", "parse_start")

        requirements: list[dict[str, Any]] = []

        # Parse mandatory requirements
        for pattern in self._requirement_patterns:
            for match in re.finditer(pattern, document_content):
                req = {
                    "req_id": f"req_{len(requirements)}",
                    "text": match.group(1).strip(),
                    "priority": "mandatory",
                    "category": self._categorize_requirement(match.group(1)),
                    "source": document_type,
                }
                requirements.append(req)

        # Parse optional/desired requirements
        desired_pattern = r"(?i)(?:preferred|desired|optional)[;: ]\s*(.+?)(?:\.|$)"
        for match in re.finditer(desired_pattern, document_content, re.MULTILINE):
            req = {
                "req_id": f"req_{len(requirements)}",
                "text": match.group(1).strip(),
                "priority": "preferred",
                "category": self._categorize_requirement(match.group(1)),
                "source": document_type,
            }
            requirements.append(req)

        self._parsed_requirements.extend(requirements)
        _log.info("Parsed %d requirements from document", len(requirements))
        _emit_records_telemetry_event("p4", "req_parser", f"parse_complete:{len(requirements)}")

        return requirements

    def _categorize_requirement(self, text: str) -> str:
        """Categorize a requirement based on keywords."""
        text_lower = text.lower()

        if any(kw in text_lower for kw in ["security", "compliance", "privacy", "gdpr", "hipaa"]):
            return "security_compliance"
        elif any(kw in text_lower for kw in ["performance", "latency", "throughput", "scalability"]):
            return "performance"
        elif any(kw in text_lower for kw in ["integration", "api", "interface", "connect"]):
            return "integration"
        elif any(kw in text_lower for kw in ["support", "maintenance", "service", "sla"]):
            return "support"
        else:
            return "functional"

    def get_requirements(
        self,
        priority: str | None = None,
        category: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get parsed requirements with optional filtering.

        Args:
            priority: Filter by priority (mandatory, preferred)
            category: Filter by category

        Returns:
            Filtered list of requirements
        """
        reqs = self._parsed_requirements.copy()

        if priority:
            reqs = [r for r in reqs if r.get("priority") == priority]
        if category:
            reqs = [r for r in reqs if r.get("category") == category]

        return reqs

    def get_requirement_summary(self) -> dict[str, int]:
        """Get a summary of parsed requirements."""
        summary: dict[str, int] = {}
        for req in self._parsed_requirements:
            cat = req.get("category", "unknown")
            summary[cat] = summary.get(cat, 0) + 1
        return summary

    def clear_requirements(self) -> None:
        """Clear the parsed requirements cache."""
        self._parsed_requirements.clear()
        _emit_records_telemetry_event("p4", "req_parser", "requirements_cleared")
