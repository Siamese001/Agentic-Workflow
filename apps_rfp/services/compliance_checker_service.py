"""
Compliance Checker Service — apps_rfp

Checks proposal compliance against RFP requirements.
Aligned with apps_lic service pattern with lifecycle trace integration.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
    _emit_routes_to_capability,
    _emit_snapshots_state,
    _emit_validates_capability,
)

_log = logging.getLogger(__name__)


class ComplianceCheckerService:
    """Service for checking proposal compliance with RFP requirements."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize the compliance checker service."""
        self.config = config or {}
        self._compliance_results: list[dict[str, Any]] = []
        _emit_snapshots_state("p0", "compliance_checker", "init")

    def check_compliance(
        self,
        requirements: list[dict[str, Any]],
        proposal_sections: list[dict[str, Any]],
        strict_mode: bool = False,
    ) -> dict[str, Any]:
        """Check proposal compliance against requirements.

        Args:
            requirements: List of parsed requirements
            proposal_sections: List of proposal sections
            strict_mode: Whether to enforce strict compliance

        Returns:
            Compliance check results
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L2_EXECUTION,
            "ComplianceCheckerService.check_compliance",
        )
        _emit_routes_to_capability("p2", "compliance_checker", "requirement_matching")
        _emit_validates_capability("p2", "compliance_checker", "content_analysis")
        _emit_records_telemetry_event("p4", "compliance_checker", "check_start")

        results: list[dict[str, Any]] = []

        for req in requirements:
            req_id = req.get("req_id", "unknown")
            req_text = req.get("text", "")
            req_priority = req.get("priority", "preferred")

            # Check if requirement is addressed in proposal
            addressed = self._requirement_addressed(req_text, proposal_sections)

            result = {
                "req_id": req_id,
                "requirement": req_text,
                "priority": req_priority,
                "addressed": addressed,
                "compliant": addressed or (req_priority != "mandatory" and not strict_mode),
                "sections_referencing": self._find_referencing_sections(req_text, proposal_sections),
            }
            results.append(result)

        # Calculate summary
        total_reqs = len(results)
        compliant_reqs = sum(1 for r in results if r.get("compliant"))
        mandatory_reqs = sum(1 for r in results if r.get("priority") == "mandatory")
        mandatory_compliant = sum(
            1 for r in results if r.get("priority") == "mandatory" and r.get("compliant")
        )

        compliance_rate = compliant_reqs / total_reqs if total_reqs > 0 else 0
        mandatory_rate = mandatory_compliant / mandatory_reqs if mandatory_reqs > 0 else 1

        summary = {
            "check_id": f"comp_{_trace_id[:8]}",
            "total_requirements": total_reqs,
            "compliant_count": compliant_reqs,
            "compliance_rate": compliance_rate,
            "mandatory_compliant": mandatory_compliant,
            "mandatory_total": mandatory_reqs,
            "mandatory_compliance_rate": mandatory_rate,
            "strict_mode": strict_mode,
            "fully_compliant": compliance_rate >= 1.0,
            "mandatory_fully_compliant": mandatory_rate >= 1.0,
            "results": results,
        }

        self._compliance_results.append(summary)

        # Apply governance gate for mandatory compliance
        if mandatory_rate < 1.0:
            _emit_applies_guardrail("p0", "compliance_checker", "mandatory_violation")

        _log.info(
            "Compliance check complete: %d/%d compliant (%.1f%%), mandatory: %d/%d",
            compliant_reqs,
            total_reqs,
            compliance_rate * 100,
            mandatory_compliant,
            mandatory_reqs,
        )
        _emit_records_telemetry_event(
            "p4",
            "compliance_checker",
            f"check_complete:{compliance_rate:.2f}",
        )

        return summary

    def _requirement_addressed(
        self,
        req_text: str,
        proposal_sections: list[dict[str, Any]],
    ) -> bool:
        """Check if a requirement is addressed in proposal sections."""
        req_keywords = set(req_text.lower().split())

        for section in proposal_sections:
            content = section.get("content", "").lower()
            # Simple keyword overlap check
            content_words = set(content.split())
            overlap = req_keywords & content_words

            # Consider addressed if significant keyword overlap
            if len(overlap) >= min(3, len(req_keywords)):
                return True

        return False

    def _find_referencing_sections(
        self,
        req_text: str,
        proposal_sections: list[dict[str, Any]],
    ) -> list[str]:
        """Find proposal sections that reference a requirement."""
        referencing: list[str] = []
        req_keywords = set(req_text.lower().split())

        for section in proposal_sections:
            section_id = section.get("section_id", "unknown")
            content = section.get("content", "").lower()
            content_words = set(content.split())

            if len(req_keywords & content_words) >= 2:
                referencing.append(section_id)

        return referencing

    def get_compliance_history(self) -> list[dict[str, Any]]:
        """Get all compliance check results."""
        return self._compliance_results.copy()

    def get_gap_analysis(self, compliance_result: dict[str, Any]) -> list[dict[str, Any]]:
        """Get detailed gap analysis for non-compliant items."""
        gaps = [
            {
                "req_id": r.get("req_id"),
                "requirement": r.get("requirement"),
                "priority": r.get("priority"),
                "reason": "Not addressed in proposal sections",
            }
            for r in compliance_result.get("results", [])
            if not r.get("compliant")
        ]
        return gaps
