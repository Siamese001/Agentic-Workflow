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
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "generation_diagnostics_engine", "execution_auth")
_emit_validates_capability("p2", "generation_diagnostics_engine", "capability_check")
_emit_routes_to_capability("p2", "generation_diagnostics_engine", "capability_route")
_emit_writes_via_uwg("p2", "generation_diagnostics_engine", "uwg_write")
_emit_blocks_direct_write("p2", "generation_diagnostics_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "generation_diagnostics_engine", "tool_invocation")
_emit_captures_execution_output("p2", "generation_diagnostics_engine", "exec_output")
_emit_dispatches_agent("p3", "generation_diagnostics_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "generation_diagnostics_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "generation_diagnostics_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "generation_diagnostics_engine", "healing_outcome")
_emit_escalates_failure("p3", "generation_diagnostics_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "generation_diagnostics_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "generation_diagnostics_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "generation_diagnostics_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "generation_diagnostics_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "generation_diagnostics_engine", "eval_metric")
_emit_stores_embedding("p4", "generation_diagnostics_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "generation_diagnostics_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "generation_diagnostics_engine", "exec_snapshot_link")
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
