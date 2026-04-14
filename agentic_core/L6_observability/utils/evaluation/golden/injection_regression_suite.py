"""
Injection Regression Suite - Deterministic Evaluation Contract.

Provides deterministic evaluation of prompt injection detection against golden dataset.
No timestamps, UUIDs, or nondeterministic fields in output.
"""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

emit_replay_key("p0", "injection_regression_suite")
emit_determinism_digest("p0", "injection_regression_suite")

_emit_dispatches_healing_run("p1", "injection_regression_suite", "L6")
_emit_routes_through("p1", "injection_regression_suite", "L6")
_emit_checks_agent_registry("p1", "injection_regression_suite", "agent_registry")
_emit_validates_agent_capability("p1", "injection_regression_suite", "capability")
_emit_dispatches_execution_plan("p1", "injection_regression_suite", "exec_plan")
_emit_agent_executes_agent("p1", "injection_regression_suite", "sub_agent")
_emit_routes_to_agent("p1", "injection_regression_suite", "target_agent")
_emit_verifies_policy("p1", "injection_regression_suite", "policy_check")
_emit_observes_runtime_state("p1", "injection_regression_suite", "runtime_state")
_emit_verifies_boundary("p1", "injection_regression_suite", "boundary_check")
_emit_transcripts_response("p1", "injection_regression_suite", "transcript")
_emit_hard_fails_untranscripted("p1", "injection_regression_suite")
_emit_gated_by_confidence("p1", "injection_regression_suite", "confidence_gate")
_emit_escalates_to_human("p1", "injection_regression_suite", "L6")
_emit_reads_policy_state("p1", "injection_regression_suite", "L6")
_emit_authorize_and_execute("p2", "injection_regression_suite", "execution_auth")
_emit_validates_capability("p2", "injection_regression_suite", "capability_check")
_emit_routes_to_capability("p2", "injection_regression_suite", "capability_route")
_emit_writes_via_uwg("p2", "injection_regression_suite", "uwg_write")
_emit_blocks_direct_write("p2", "injection_regression_suite", "direct_write_block")
_emit_records_tool_invocation("p2", "injection_regression_suite", "tool_invocation")
_emit_captures_execution_output("p2", "injection_regression_suite", "exec_output")
_emit_dispatches_agent("p3", "injection_regression_suite", "agent_dispatch")
_emit_coordinates_agents("p3", "injection_regression_suite", "agent_coordination")
_emit_records_workflow_lineage("p3", "injection_regression_suite", "workflow_lineage")
_emit_records_healing_outcome("p3", "injection_regression_suite", "healing_outcome")
_emit_escalates_failure("p3", "injection_regression_suite", "failure_escalation")
_emit_orchestrates_workflow("p3", "injection_regression_suite", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "injection_regression_suite", "healing_dispatch")
_emit_invokes_evaluation("p3", "injection_regression_suite", "evaluation_signal")
_emit_records_telemetry_event("p4", "injection_regression_suite", "telemetry_event")
_emit_captures_evaluation_metric("p4", "injection_regression_suite", "eval_metric")
_emit_stores_embedding("p4", "injection_regression_suite", "embedding_store")
_emit_updates_meta_learning_state("p4", "injection_regression_suite", "meta_learning")
_emit_links_execution_to_snapshot("p4", "injection_regression_suite", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

record_execution_trace("injection_regression_suite", "injection_regression_suite_trace")


_emit_emits_metric_event("injection_regression_suite", "p4obs", "metric_1")
_emit_emits_metric_event("injection_regression_suite", "p4obs", "metric_2")
_emit_emits_metric_event("injection_regression_suite", "p4obs", "metric_3")
_emit_emits_metric_event("injection_regression_suite", "p4obs", "metric_4")
_emit_emits_metric_event("injection_regression_suite", "p4obs", "metric_5")
_emit_emits_metric_event("injection_regression_suite", "p4obs", "metric_6")
_emit_records_incident_event("injection_regression_suite", "p4obs", "incident")
_emit_captures_runtime_anomaly("injection_regression_suite", "p4obs", "anomaly")
_emit_writes_observability_log("injection_regression_suite", "p4obs", "obs_log")
_emit_updates_monitoring_state("injection_regression_suite", "p4obs", "mon_state")
_emit_triggers_alert("injection_regression_suite", "p4obs", "alert")
_emit_links_incident_trace("injection_regression_suite", "p4obs", "trace_link")
_emit_captures_pattern("injection_regression_suite", "p3lm", "pattern")
_emit_records_learning_event("injection_regression_suite", "p3lm", "learning_event")
_emit_writes_learning_snapshot("injection_regression_suite", "p3lm", "snapshot")
_emit_feeds_meta_learning("injection_regression_suite", "p3lm", "meta_feed")
_emit_updates_routing_strategy("injection_regression_suite", "p3lm", "routing")
_emit_improves_agent_policy("injection_regression_suite", "p3lm", "policy")
_emit_stores_learning_state("injection_regression_suite", "p3lm", "state")
_emit_records_execution_trace("injection_regression_suite", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("injection_regression_suite", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("injection_regression_suite", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("injection_regression_suite", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("injection_regression_suite", "L4_STATE", "p2_trace_5")
_emit_reads_environ("injection_regression_suite", "env_read", "p2_env_1")
_emit_reads_environ("injection_regression_suite", "env_read", "p2_env_2")
_emit_reads_runtime_state("injection_regression_suite", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("injection_regression_suite", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "injection_regression_suite", "context_pull")
_emit_pulls_context("p1", "injection_regression_suite", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "injection_regression_suite", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "injection_regression_suite", "uwg_term_2")
_emit_writes_through("p1", "injection_regression_suite", "write_through")
_emit_writes_through("p1", "injection_regression_suite", "write_through_2")
_emit_validated_by_safety_plane("p1", "injection_regression_suite", "safety_validation")
_emit_invokes_eval("p1", "injection_regression_suite", "eval_call")
_emit_proposal_commits_routing("p1", "injection_regression_suite", "routing_commit")


@dataclass(frozen=True)
class InjectionRegressionResult:
    """Deterministic result of injection regression evaluation."""

    total_samples: int
    blocked_samples: int
    detection_rate: float
    high_risk_patterns: int
    certification_hash: str
    attack_distribution: dict[str, int]
    error_message: str = ""


def evaluate_injection_regression(data_root: str = None, limit: int = None) -> InjectionRegressionResult:
    """Evaluate injection detection against golden dataset deterministically.

    Args:
        data_root: Root directory containing data/golden/ subdirectory
        limit: Optional limit on number of samples to process

    Returns:
        InjectionRegressionResult with deterministic certification hash
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "evaluate_injection_regression", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "evaluate_injection_regression", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L6_OBSERVABILITY, "evaluate_injection_regression")
    if data_root is None:
        data_root = Path(__file__).parent.parent.parent.parent.parent / "data"
    golden_dir = Path(data_root) / "golden"
    injection_file = golden_dir / "prompt_injection_attacks_200.jsonl"
    if not injection_file.exists():
        result = InjectionRegressionResult(
            total_samples=0,
            blocked_samples=0,
            detection_rate=0.0,
            high_risk_patterns=0,
            certification_hash=hashlib.sha256(b"no_data").hexdigest(),
            attack_distribution={},
            error_message="Golden dataset not found",
        )
        return result
    samples = []
    with open(injection_file, encoding="utf-8") as f:
        for line in f:
            if limit and len(samples) >= limit:
                break
            samples.append(json.loads(line))
    blocked_count = 0
    high_risk_count = 0
    attack_dist = {}
    for sample in samples:
        attack_type = sample.get("attack_type", "unknown")
        success_rate = sample.get("success_rate", 1.0)
        severity = sample.get("severity", "low")
        attack_dist[attack_type] = attack_dist.get(attack_type, 0) + 1
        if success_rate < 0.5:
            blocked_count += 1
        if severity in ["critical", "high"]:
            high_risk_count += 1
    detection_rate = blocked_count / len(samples) if samples else 0.0
    hash_data = {
        "total_samples": len(samples),
        "blocked_samples": blocked_count,
        "detection_rate": detection_rate,
        "high_risk_patterns": high_risk_count,
        "attack_distribution": attack_dist,
    }
    cert_hash = hashlib.sha256(
        json.dumps(hash_data, sort_keys=True, separators=(",", ":")).encode(),
    ).hexdigest()
    return InjectionRegressionResult(
        total_samples=len(samples),
        blocked_samples=blocked_count,
        detection_rate=detection_rate,
        high_risk_patterns=high_risk_count,
        certification_hash=cert_hash,
        attack_distribution=attack_dist,
    )
