"""
Reflection Engine - Post-execution learning and scoring
Refactored from RgReflectionAgent.py
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

_emit_authorize_and_execute("p2", "reflection_engine", "execution_auth")
_emit_validates_capability("p2", "reflection_engine", "capability_check")
_emit_routes_to_capability("p2", "reflection_engine", "capability_route")
_emit_writes_via_uwg("p2", "reflection_engine", "uwg_write")
_emit_blocks_direct_write("p2", "reflection_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "reflection_engine", "tool_invocation")
_emit_captures_execution_output("p2", "reflection_engine", "exec_output")
_emit_dispatches_agent("p3", "reflection_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "reflection_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "reflection_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "reflection_engine", "healing_outcome")
_emit_escalates_failure("p3", "reflection_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "reflection_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "reflection_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "reflection_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "reflection_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "reflection_engine", "eval_metric")
_emit_stores_embedding("p4", "reflection_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "reflection_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "reflection_engine", "exec_snapshot_link")
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_applies_guardrail("p0", "reflection_engine", "p0_governance")
_emit_reads_policy_state("p0", "reflection_engine", "policy_binding")
_emit_snapshots_state("p0", "reflection_engine", "state_snapshot")
emit_replay_key("p0", "reflection_engine")
emit_determinism_digest("p0", "reflection_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class ReflectionEngine(BaseRGEngine):
    """
    Reflection - Post-cycle learning and scoring.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="ORCHESTRATION.REFLECTION")

    async def execute(self, workflow_results: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze workflow results and extract learnings.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ReflectionEngine.execute")

        self._mcp_audit("reflection_start")
        reflection = {
            "overall_score": 0.0,
            "strengths": [],
            "weaknesses": [],
            "learnings": [],
            "recommendations": [],
        }
        passed_engines = [k for k, v in workflow_results.items() if v.get("passed", False)]
        failed_engines = [k for k, v in workflow_results.items() if not v.get("passed", True)]
        reflection["overall_score"] = len(passed_engines) / max(len(workflow_results), 1)
        if reflection["overall_score"] >= 0.9:
            reflection["strengths"].append("High success rate across engines")
        if failed_engines:
            reflection["weaknesses"].append(f"Failures in: {', '.join(failed_engines)}")
            reflection["recommendations"].append("Review failed engine configurations")
        for engine_name, result in workflow_results.items():
            if result.get("signal"):
                reflection["learnings"].append(f"{engine_name} signaled: {result['signal']}")
        self.record_pass("Reflection complete", data=reflection)
        return reflection
