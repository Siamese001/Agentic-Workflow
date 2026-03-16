"""
agentic_core/L0_routing/config/ssot_tier_constants.py

L0-accessible copies of the SSOT routing/healing tier thresholds.

These constants are copied here from L2_execution/healers/healing_tier_config.py
so that L0 scripts (_ssot_reporting.py, _ssot_routing.py) can read them without
importing across the L0→L2 layer boundary.

Source of truth: agentic_core/L2_execution/healers/healing_tier_config.py
ADG fix: A-06 (violates L0→L2 in _ssot_reporting.py and _ssot_routing.py)
"""

from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

_emit_reads_policy_state("p1", "ssot_tier_constants", "L0")
_emit_escalates_to_human("p1", "ssot_tier_constants", "L0")
_emit_routes_through("p1", "ssot_tier_constants", "L0")
_emit_dispatches_healing_run("p1", "ssot_tier_constants", "L0")
_emit_records_execution_trace("p0", "evidence", "ssot_tier_constants")
_emit_applies_guardrail("p0", "ssot_tier_constants", "p0_governance")
_emit_snapshots_state("p0", "ssot_tier_constants", "state_snapshot")
emit_replay_key("p0", "ssot_tier_constants")
emit_determinism_digest("p0", "ssot_tier_constants")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ssot_tier_constants", "execution_auth")
_emit_validates_capability("p2", "ssot_tier_constants", "capability_check")
_emit_routes_to_capability("p2", "ssot_tier_constants", "capability_route")
_emit_writes_via_uwg("p2", "ssot_tier_constants", "uwg_write")
_emit_blocks_direct_write("p2", "ssot_tier_constants", "direct_write_block")
_emit_records_tool_invocation("p2", "ssot_tier_constants", "tool_invocation")
_emit_captures_execution_output("p2", "ssot_tier_constants", "exec_output")
_emit_dispatches_agent("p3", "ssot_tier_constants", "agent_dispatch")
_emit_coordinates_agents("p3", "ssot_tier_constants", "agent_coordination")
_emit_records_workflow_lineage("p3", "ssot_tier_constants", "workflow_lineage")
_emit_records_healing_outcome("p3", "ssot_tier_constants", "healing_outcome")
_emit_escalates_failure("p3", "ssot_tier_constants", "failure_escalation")
_emit_orchestrates_workflow("p3", "ssot_tier_constants", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ssot_tier_constants", "healing_dispatch")
_emit_invokes_evaluation("p3", "ssot_tier_constants", "evaluation_signal")
_emit_records_telemetry_event("p4", "ssot_tier_constants", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ssot_tier_constants", "eval_metric")
_emit_stores_embedding("p4", "ssot_tier_constants", "embedding_store")
_emit_updates_meta_learning_state("p4", "ssot_tier_constants", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ssot_tier_constants", "exec_snapshot_link")

# FIXED THRESHOLDS - IMMUTABLE BY META-LEARNING
HEALING_CONFIDENCE_X: float = 0.80  # Upper threshold: conf > X  → DETERMINISTIC
HEALING_CONFIDENCE_Y: float = 0.50  # Lower threshold: conf <= Y → GEMINI 2.5 Pro

# SSOT score thresholds for integer-score routing (S = 3C+4B+3A+2N+4F)
SSOT_SCORE_THRESHOLD_DET: int = 13  # S <= 13  → DETERMINISTIC
SSOT_SCORE_THRESHOLD_QWEN: int = 26  # S <= 26  → QWEN; S > 26 → GEMINI

# Qwen 14B model identifier
QWEN_14B_MODEL_ID: str = "Qwen/Qwen2.5-14B-Instruct-GPTQ-Int4"

__all__ = [
    "HEALING_CONFIDENCE_X",
    "HEALING_CONFIDENCE_Y",
    "SSOT_SCORE_THRESHOLD_DET",
    "SSOT_SCORE_THRESHOLD_QWEN",
    "QWEN_14B_MODEL_ID",
]
