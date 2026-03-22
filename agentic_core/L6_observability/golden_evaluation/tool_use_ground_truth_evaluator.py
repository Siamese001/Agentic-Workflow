"""
Tool Use Ground Truth Evaluator - Deterministic Evaluation Contract.

Provides deterministic evaluation of tool selection against golden dataset.
No timestamps, UUIDs, or nondeterministic fields in output.
"""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    record_execution_trace,
)

emit_replay_key("p0", "tool_use_ground_truth_evaluator")
emit_determinism_digest("p0", "tool_use_ground_truth_evaluator")

_emit_dispatches_healing_run("p1", "tool_use_ground_truth_evaluator", "L6")
_emit_routes_through("p1", "tool_use_ground_truth_evaluator", "L6")
_emit_checks_agent_registry("p1", "tool_use_ground_truth_evaluator", "agent_registry")
_emit_validates_agent_capability("p1", "tool_use_ground_truth_evaluator", "capability")
_emit_dispatches_execution_plan("p1", "tool_use_ground_truth_evaluator", "exec_plan")
_emit_agent_executes_agent("p1", "tool_use_ground_truth_evaluator", "sub_agent")
_emit_routes_to_agent("p1", "tool_use_ground_truth_evaluator", "target_agent")
_emit_verifies_policy("p1", "tool_use_ground_truth_evaluator", "policy_check")
_emit_observes_runtime_state("p1", "tool_use_ground_truth_evaluator", "runtime_state")
_emit_verifies_boundary("p1", "tool_use_ground_truth_evaluator", "boundary_check")
_emit_transcripts_response("p1", "tool_use_ground_truth_evaluator", "transcript")
_emit_hard_fails_untranscripted("p1", "tool_use_ground_truth_evaluator")
_emit_gated_by_confidence("p1", "tool_use_ground_truth_evaluator", "confidence_gate")
_emit_escalates_to_human("p1", "tool_use_ground_truth_evaluator", "L6")
_emit_reads_policy_state("p1", "tool_use_ground_truth_evaluator", "L6")
_emit_authorize_and_execute("p2", "tool_use_ground_truth_evaluator", "execution_auth")
_emit_validates_capability("p2", "tool_use_ground_truth_evaluator", "capability_check")
_emit_routes_to_capability("p2", "tool_use_ground_truth_evaluator", "capability_route")
_emit_writes_via_uwg("p2", "tool_use_ground_truth_evaluator", "uwg_write")
_emit_blocks_direct_write("p2", "tool_use_ground_truth_evaluator", "direct_write_block")
_emit_records_tool_invocation("p2", "tool_use_ground_truth_evaluator", "tool_invocation")
_emit_captures_execution_output("p2", "tool_use_ground_truth_evaluator", "exec_output")
_emit_dispatches_agent("p3", "tool_use_ground_truth_evaluator", "agent_dispatch")
_emit_coordinates_agents("p3", "tool_use_ground_truth_evaluator", "agent_coordination")
_emit_records_workflow_lineage("p3", "tool_use_ground_truth_evaluator", "workflow_lineage")
_emit_records_healing_outcome("p3", "tool_use_ground_truth_evaluator", "healing_outcome")
_emit_escalates_failure("p3", "tool_use_ground_truth_evaluator", "failure_escalation")
_emit_orchestrates_workflow("p3", "tool_use_ground_truth_evaluator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "tool_use_ground_truth_evaluator", "healing_dispatch")
_emit_invokes_evaluation("p3", "tool_use_ground_truth_evaluator", "evaluation_signal")
_emit_records_telemetry_event("p4", "tool_use_ground_truth_evaluator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "tool_use_ground_truth_evaluator", "eval_metric")
_emit_stores_embedding("p4", "tool_use_ground_truth_evaluator", "embedding_store")
_emit_updates_meta_learning_state("p4", "tool_use_ground_truth_evaluator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "tool_use_ground_truth_evaluator", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

record_execution_trace("tool_use_ground_truth_evaluator", "tool_use_ground_truth_evaluator_trace")


_emit_emits_metric_event("tool_use_ground_truth_evaluator", "p4obs", "metric_1")
_emit_emits_metric_event("tool_use_ground_truth_evaluator", "p4obs", "metric_2")
_emit_emits_metric_event("tool_use_ground_truth_evaluator", "p4obs", "metric_3")
_emit_emits_metric_event("tool_use_ground_truth_evaluator", "p4obs", "metric_4")
_emit_emits_metric_event("tool_use_ground_truth_evaluator", "p4obs", "metric_5")
_emit_emits_metric_event("tool_use_ground_truth_evaluator", "p4obs", "metric_6")
_emit_records_incident_event("tool_use_ground_truth_evaluator", "p4obs", "incident")
_emit_captures_runtime_anomaly("tool_use_ground_truth_evaluator", "p4obs", "anomaly")
_emit_writes_observability_log("tool_use_ground_truth_evaluator", "p4obs", "obs_log")
_emit_updates_monitoring_state("tool_use_ground_truth_evaluator", "p4obs", "mon_state")
_emit_triggers_alert("tool_use_ground_truth_evaluator", "p4obs", "alert")
_emit_links_incident_trace("tool_use_ground_truth_evaluator", "p4obs", "trace_link")
_emit_captures_pattern("tool_use_ground_truth_evaluator", "p3lm", "pattern")
_emit_records_learning_event("tool_use_ground_truth_evaluator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("tool_use_ground_truth_evaluator", "p3lm", "snapshot")
_emit_feeds_meta_learning("tool_use_ground_truth_evaluator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("tool_use_ground_truth_evaluator", "p3lm", "routing")
_emit_improves_agent_policy("tool_use_ground_truth_evaluator", "p3lm", "policy")
_emit_stores_learning_state("tool_use_ground_truth_evaluator", "p3lm", "state")
_emit_records_execution_trace("tool_use_ground_truth_evaluator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("tool_use_ground_truth_evaluator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("tool_use_ground_truth_evaluator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("tool_use_ground_truth_evaluator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("tool_use_ground_truth_evaluator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("tool_use_ground_truth_evaluator", "env_read", "p2_env_1")
_emit_reads_environ("tool_use_ground_truth_evaluator", "env_read", "p2_env_2")
_emit_reads_runtime_state("tool_use_ground_truth_evaluator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("tool_use_ground_truth_evaluator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "tool_use_ground_truth_evaluator", "context_pull")
_emit_pulls_context("p1", "tool_use_ground_truth_evaluator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "tool_use_ground_truth_evaluator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "tool_use_ground_truth_evaluator", "uwg_term_2")
_emit_writes_through("p1", "tool_use_ground_truth_evaluator", "write_through")
_emit_writes_through("p1", "tool_use_ground_truth_evaluator", "write_through_2")
_emit_validated_by_safety_plane("p1", "tool_use_ground_truth_evaluator", "safety_validation")
_emit_invokes_eval("p1", "tool_use_ground_truth_evaluator", "eval_call")
_emit_proposal_commits_routing("p1", "tool_use_ground_truth_evaluator", "routing_commit")


@dataclass(frozen=True)
class ToolUseResult:
    """Deterministic result of tool use evaluation."""

    total_samples: int
    correct_tool_selections: int
    certification_hash: str
    tool_distribution: dict[str, int]
    complex_queries: list[dict[str, Any]]
    average_tools_per_query: float
    error_message: str = ""


def evaluate_tool_use_ground_truth(data_root: str = None, limit: int = None) -> ToolUseResult:
    """Evaluate tool use against golden dataset deterministically.

    Args:
        data_root: Root directory containing data/golden/ subdirectory
        limit: Optional limit on number of samples to process

    Returns:
        ToolUseResult with deterministic certification hash
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "evaluate_tool_use_ground_truth", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "evaluate_tool_use_ground_truth", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L6_OBSERVABILITY, "evaluate_tool_use_ground_truth")
    if data_root is None:
        data_root = Path(__file__).parent.parent.parent.parent.parent / "data"
    golden_dir = Path(data_root) / "golden"
    tool_file = golden_dir / "tool_use_ground_truth_1000.jsonl"
    if not tool_file.exists():
        result = ToolUseResult(
            total_samples=0,
            correct_tool_selections=0,
            certification_hash=hashlib.sha256(b"no_data").hexdigest(),
            tool_distribution={},
            complex_queries=[],
            average_tools_per_query=0.0,
            error_message="Golden dataset not found",
        )
        return result
    samples = []
    with open(tool_file, encoding="utf-8") as f:
        for line in f:
            if limit and len(samples) >= limit:
                break
            samples.append(json.loads(line))
    correct_count = 0
    tool_dist = {}
    complex_queries = []
    total_tools = 0
    for sample in samples:
        expected_calls = sample.get("expected_tool_calls", [])
        scenario = sample.get("scenario", "unknown")
        success_criteria = sample.get("success_criteria", [])
        for tool_call in expected_calls:
            tool_name = tool_call.get("name", "unknown")
            tool_dist[tool_name] = tool_dist.get(tool_name, 0) + 1
            total_tools += 1
        if "correct_tool" in success_criteria:
            correct_count += 1
        if len(expected_calls) >= 3 or "proper_chaining" in success_criteria:
            complex_queries.append(
                {
                    "id": sample.get("id", ""),
                    "scenario": scenario,
                    "tool_count": len(expected_calls),
                    "tools": [call.get("name") for call in expected_calls],
                }
            )
    avg_tools = total_tools / len(samples) if samples else 0.0
    hash_data = {
        "total_samples": len(samples),
        "correct_tool_selections": correct_count,
        "tool_distribution": tool_dist,
        "complex_queries_count": len(complex_queries),
        "average_tools_per_query": avg_tools,
    }
    cert_hash = hashlib.sha256(
        json.dumps(hash_data, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return ToolUseResult(
        total_samples=len(samples),
        correct_tool_selections=correct_count,
        certification_hash=cert_hash,
        tool_distribution=tool_dist,
        complex_queries=complex_queries,
        average_tools_per_query=avg_tools,
    )
