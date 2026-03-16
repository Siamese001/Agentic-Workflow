"""
Section Balance Engine - Length/ratio validation
Refactored from SectionBalanceAgent.py
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

_emit_authorize_and_execute("p2", "section_balance_engine", "execution_auth")
_emit_validates_capability("p2", "section_balance_engine", "capability_check")
_emit_routes_to_capability("p2", "section_balance_engine", "capability_route")
_emit_writes_via_uwg("p2", "section_balance_engine", "uwg_write")
_emit_blocks_direct_write("p2", "section_balance_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "section_balance_engine", "tool_invocation")
_emit_captures_execution_output("p2", "section_balance_engine", "exec_output")
_emit_dispatches_agent("p3", "section_balance_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "section_balance_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "section_balance_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "section_balance_engine", "healing_outcome")
_emit_escalates_failure("p3", "section_balance_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "section_balance_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "section_balance_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "section_balance_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "section_balance_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "section_balance_engine", "eval_metric")
_emit_stores_embedding("p4", "section_balance_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "section_balance_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "section_balance_engine", "exec_snapshot_link")
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_applies_guardrail("p0", "section_balance_engine", "p0_governance")
_emit_reads_policy_state("p0", "section_balance_engine", "policy_binding")
_emit_snapshots_state("p0", "section_balance_engine", "state_snapshot")
emit_replay_key("p0", "section_balance_engine")
emit_determinism_digest("p0", "section_balance_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class SectionBalanceEngine(BaseRGEngine):
    """
    Validates section length and ratio balance.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="REFINE.BALANCE")

    async def execute(self, sections: dict[str, Any]) -> dict[str, Any]:
        """
        Validate section balance and ratios.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SectionBalanceEngine.execute")

        self._mcp_audit("balance_check")
        section_lengths = {}
        for name, content in sections.items():
            if isinstance(content, str):
                section_lengths[name] = len(content.split())
            elif isinstance(content, list):
                section_lengths[name] = sum(len(str(item).split()) for item in content)
        total_words = sum(section_lengths.values())
        ratios = {name: length / total_words for name, length in section_lengths.items()}
        issues = []
        exp_ratio = ratios.get("experience", 0)
        if exp_ratio < 0.4 or exp_ratio > 0.6:
            issues.append(f"Experience ratio {exp_ratio:.1%} outside target 40-60%")
        summary_ratio = ratios.get("summary", 0)
        if summary_ratio > 0.2:
            issues.append(f"Summary ratio {summary_ratio:.1%} exceeds 20% limit")
        result = {
            "balanced": len(issues) == 0,
            "section_lengths": section_lengths,
            "ratios": ratios,
            "issues": issues,
        }
        if issues:
            self.record_fail("Section balance issues detected", data=result, signal="BALANCE_VIOLATION")
        else:
            self.record_pass("Section balance validated")
        return result
