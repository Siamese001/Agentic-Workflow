"""
Generation Diagnostics Engine - Failure analysis
Refactored from diagnose_generation_issues.py
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_applies_guardrail("p0", "generation_diagnostics_engine", "p0_governance")
_emit_reads_policy_state("p0", "generation_diagnostics_engine", "policy_binding")
_emit_snapshots_state("p0", "generation_diagnostics_engine", "state_snapshot")
emit_replay_key("p0", "generation_diagnostics_engine")
emit_determinism_digest("p0", "generation_diagnostics_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class GenerationDiagnosticsEngine(BaseRGEngine):
    """
    Diagnoses generation failures and provides remediation suggestions.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="QUALITY.DIAGNOSTICS")

    async def execute(self, failure_context: dict[str, Any]) -> dict[str, Any]:
        """
        Diagnose generation failure and suggest fixes.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "GenerationDiagnosticsEngine.execute")

        self._mcp_audit("diagnostics_start")
        diagnosis = {"root_cause": "unknown", "contributing_factors": [], "remediation_steps": []}
        if failure_context.get("empty_output"):
            diagnosis["root_cause"] = "llm_timeout_or_budget"
            diagnosis["remediation_steps"].append("Increase timeout threshold")
            diagnosis["remediation_steps"].append("Simplify prompt")
        if failure_context.get("invalid_format"):
            diagnosis["root_cause"] = "parsing_failure"
            diagnosis["remediation_steps"].append("Add format constraints to prompt")
        if failure_context.get("quality_score", 1.0) < 0.5:
            diagnosis["root_cause"] = "insufficient_context"
            diagnosis["contributing_factors"].append("Low quality score")
            diagnosis["remediation_steps"].append("Enrich input context")
        self.record_pass("Diagnostics complete", data=diagnosis)
        return diagnosis
