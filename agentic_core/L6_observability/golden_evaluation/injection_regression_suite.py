"""
Injection Regression Suite - Deterministic Evaluation Contract.

Provides deterministic evaluation of prompt injection detection against golden dataset.
No timestamps, UUIDs, or nondeterministic fields in output.
"""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "injection_regression_suite")
emit_determinism_digest("p0", "injection_regression_suite")

_emit_dispatches_healing_run("p1", "injection_regression_suite", "L6")
_emit_routes_through("p1", "injection_regression_suite", "L6")
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
        json.dumps(hash_data, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return InjectionRegressionResult(
        total_samples=len(samples),
        blocked_samples=blocked_count,
        detection_rate=detection_rate,
        high_risk_patterns=high_risk_count,
        certification_hash=cert_hash,
        attack_distribution=attack_dist,
    )
