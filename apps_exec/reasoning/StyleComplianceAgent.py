"""
Style Compliance Agent — apps_exec/reasoning

Agent for validating style compliance in executive briefs.
Aligned with apps_lic agent patterns with lifecycle trace integration.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_agent,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
    _emit_snapshots_state,
    emit_determinism_digest,
    emit_replay_key,
)

_log = logging.getLogger(__name__)


class StyleComplianceAgent:
    """Agent for validating style compliance."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self._forbidden_phrases = self.config.get("forbidden_phrases", ["synergy", "leverage"])

        emit_replay_key("style_compliance", "agent_init")
        emit_determinism_digest("style_compliance", "agent_init")
        _emit_applies_guardrail("p0", "style_compliance_agent", "agent_init")
        _emit_snapshots_state("p0", "style_compliance_agent", "agent_state")

    async def validate_style(
        self,
        brief_content: str,
        persona_id: str,
    ) -> dict[str, Any]:
        """Validate style compliance of a brief."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "StyleComplianceAgent.validate_style"
        )
        _emit_orchestrates_workflow("p3", "style_compliance_agent", "validation_workflow")
        _emit_dispatches_agent("p3", "style_compliance_agent", "validation_dispatch")
        _emit_records_telemetry_event("p4", "style_compliance_agent", "validation_start")

        violations: list[str] = []

        for phrase in self._forbidden_phrases:
            if phrase.lower() in brief_content.lower():
                violations.append(f"Forbidden phrase detected: '{phrase}'")

        compliant = len(violations) == 0

        if not compliant:
            _emit_applies_guardrail("p0", "style_compliance_agent", "style_violation")

        _log.info("Style validation %s: %d violations", "PASSED" if compliant else "FAILED", len(violations))
        _emit_records_telemetry_event(
            "p4", "style_compliance_agent", f"validation_complete:{'compliant' if compliant else 'violations'}"
        )

        return {
            "success": True,
            "trace_id": _trace_id,
            "compliant": compliant,
            "violations": violations,
            "persona_id": persona_id,
        }

    @staticmethod
    def _make_trace_id(persona_id: str) -> str:
        raw = f"style:{persona_id}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
