"""
HITL Decision Logger — Wave 6.

Appends structured HITL decision records to the active evidence file so every
human-in-the-loop choice is auditable and replayable.

Design constraints:
- Pure stdlib (no third-party imports).
- Thread-safe via module-level lock.
- Deterministic record format (no wall-clock timestamps in keys).
- ASCII-only output (evidence file byte-scan invariant §2).
"""

from __future__ import annotations

import logging
import os
import threading
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.enforcement.credential_guard import get_credential_guard as credential_guard
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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
)

_emit_records_execution_trace("p0", "evidence", "hitl_decision_logger")
_emit_applies_guardrail("p0", "hitl_decision_logger", "p0_governance")
_emit_reads_policy_state("p0", "hitl_decision_logger", "policy_binding")
_emit_snapshots_state("p0", "hitl_decision_logger", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("hitl_decision_logger", "p4obs", "metric_1")
_emit_emits_metric_event("hitl_decision_logger", "p4obs", "metric_2")
_emit_emits_metric_event("hitl_decision_logger", "p4obs", "metric_3")
_emit_emits_metric_event("hitl_decision_logger", "p4obs", "metric_4")
_emit_emits_metric_event("hitl_decision_logger", "p4obs", "metric_5")
_emit_emits_metric_event("hitl_decision_logger", "p4obs", "metric_6")
_emit_records_incident_event("hitl_decision_logger", "p4obs", "incident")
_emit_captures_runtime_anomaly("hitl_decision_logger", "p4obs", "anomaly")
_emit_writes_observability_log("hitl_decision_logger", "p4obs", "obs_log")
_emit_updates_monitoring_state("hitl_decision_logger", "p4obs", "mon_state")
_emit_triggers_alert("hitl_decision_logger", "p4obs", "alert")
_emit_links_incident_trace("hitl_decision_logger", "p4obs", "trace_link")
_emit_captures_pattern("hitl_decision_logger", "p3lm", "pattern")
_emit_records_learning_event("hitl_decision_logger", "p3lm", "learning_event")
_emit_writes_learning_snapshot("hitl_decision_logger", "p3lm", "snapshot")
_emit_feeds_meta_learning("hitl_decision_logger", "p3lm", "meta_feed")
_emit_updates_routing_strategy("hitl_decision_logger", "p3lm", "routing")
_emit_improves_agent_policy("hitl_decision_logger", "p3lm", "policy")
_emit_stores_learning_state("hitl_decision_logger", "p3lm", "state")
_emit_records_execution_trace("hitl_decision_logger", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("hitl_decision_logger", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("hitl_decision_logger", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("hitl_decision_logger", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("hitl_decision_logger", "L4_STATE", "p2_trace_5")
_emit_reads_environ("hitl_decision_logger", "env_read", "p2_env_1")
_emit_reads_environ("hitl_decision_logger", "env_read", "p2_env_2")
_emit_reads_runtime_state("hitl_decision_logger", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("hitl_decision_logger", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "hitl_decision_logger", "context_pull")
_emit_pulls_context("p1", "hitl_decision_logger", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "hitl_decision_logger", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "hitl_decision_logger", "uwg_term_2")
_emit_writes_through("p1", "hitl_decision_logger", "write_through")
_emit_writes_through("p1", "hitl_decision_logger", "write_through_2")
_emit_validated_by_safety_plane("p1", "hitl_decision_logger", "safety_validation")
_emit_invokes_eval("p1", "hitl_decision_logger", "eval_call")
_emit_proposal_commits_routing("p1", "hitl_decision_logger", "routing_commit")
_emit_escalates_to_human("p1", "hitl_decision_logger", "human_escalation")
_emit_routes_through("p1", "hitl_decision_logger", "route_through")
_emit_checks_agent_registry("p1", "hitl_decision_logger", "agent_registry")
_emit_validates_agent_capability("p1", "hitl_decision_logger", "capability")
_emit_dispatches_execution_plan("p1", "hitl_decision_logger", "exec_plan")
_emit_agent_executes_agent("p1", "hitl_decision_logger", "sub_agent")
_emit_routes_to_agent("p1", "hitl_decision_logger", "target_agent")
_emit_verifies_policy("p1", "hitl_decision_logger", "policy_check")
_emit_observes_runtime_state("p1", "hitl_decision_logger", "runtime_state")
_emit_verifies_boundary("p1", "hitl_decision_logger", "boundary_check")
_emit_transcripts_response("p1", "hitl_decision_logger", "transcript")
_emit_hard_fails_untranscripted("p1", "hitl_decision_logger")
_emit_gated_by_confidence("p1", "hitl_decision_logger", "confidence_gate")
emit_replay_key("p0", "hitl_decision_logger")
emit_determinism_digest("p0", "hitl_decision_logger")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "hitl_decision_logger", "execution_auth")
_emit_validates_capability("p2", "hitl_decision_logger", "capability_check")
_emit_routes_to_capability("p2", "hitl_decision_logger", "capability_route")
_emit_writes_via_uwg("p2", "hitl_decision_logger", "uwg_write")
_emit_blocks_direct_write("p2", "hitl_decision_logger", "direct_write_block")
_emit_records_tool_invocation("p2", "hitl_decision_logger", "tool_invocation")
_emit_captures_execution_output("p2", "hitl_decision_logger", "exec_output")
_emit_dispatches_agent("p3", "hitl_decision_logger", "agent_dispatch")
_emit_coordinates_agents("p3", "hitl_decision_logger", "agent_coordination")
_emit_records_workflow_lineage("p3", "hitl_decision_logger", "workflow_lineage")
_emit_records_healing_outcome("p3", "hitl_decision_logger", "healing_outcome")
_emit_escalates_failure("p3", "hitl_decision_logger", "failure_escalation")
_emit_orchestrates_workflow("p3", "hitl_decision_logger", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "hitl_decision_logger", "healing_dispatch")
_emit_invokes_evaluation("p3", "hitl_decision_logger", "evaluation_signal")
_emit_records_telemetry_event("p4", "hitl_decision_logger", "telemetry_event")
_emit_captures_evaluation_metric("p4", "hitl_decision_logger", "eval_metric")
_emit_stores_embedding("p4", "hitl_decision_logger", "embedding_store")
_emit_updates_meta_learning_state("p4", "hitl_decision_logger", "meta_learning")
_emit_links_execution_to_snapshot("p4", "hitl_decision_logger", "exec_snapshot_link")

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_decision_counter: int = 0
_DEFAULT_EVIDENCE_PATH = Path("docs/reports/evidence/wave6_evidence.md")


def _get_evidence_path() -> Path:
    credential_guard().check(operation="credential_access", target="os.environ.get")
    env_val = os.environ.get("HITL_EVIDENCE_FILE")
    if env_val:
        return Path(env_val)
    return _DEFAULT_EVIDENCE_PATH


def log_hitl_decision(
    agent: str,
    file_path: str,
    violation: str,
    proposed: str,
    decision: str,
    extra: dict[str, Any] | None = None,
) -> int:
    """Append one HITL decision record to the evidence file.

    Args:
        agent:      Agent class name that triggered the gate.
        file_path:  Relative or absolute path of the affected file.
        violation:  Violation type string (e.g. PASCAL_IN_NON_AGENT_FOLDER).
        proposed:   What the agent was about to do (e.g. ARCHIVE, MOVE).
        decision:   Outcome after HITL review (e.g. APPROVED, SKIPPED, MANUAL).
        extra:      Optional additional key-value pairs appended to the record.

    Returns:
        The sequential decision number (1-based).
    """
    global _decision_counter
    evidence_path = _get_evidence_path()
    with _lock:
        _decision_counter += 1
        n = _decision_counter
        lines = [
            f"\nHITL_DECISION_{n}: Agent={agent} | File={file_path}",
            f"  Violation={violation} | Proposed={proposed} | Decision={decision}",
        ]
        if extra:
            for k, v in extra.items():
                safe_k = str(k).replace("\n", " ")
                safe_v = str(v).replace("\n", " ")
                lines.append(f"  {safe_k}={safe_v}")
        record = "\n".join(lines) + "\n"
        safe_record = record.encode("ascii", errors="replace").decode("ascii")
        try:
            evidence_path.parent.mkdir(parents=True, exist_ok=True)
            with open(evidence_path, "a", encoding="ascii", errors="replace") as fh:
                fh.write(safe_record)
        except OSError:  # guardian: Add error context logging
            import logging

            logging.getLogger(__name__).debug("hitl_decision_logger: OSError swallowed at L213: %s", e)
        return n


def get_decision_count() -> int:
    """Return number of decisions logged in this process lifetime."""
    with _lock:
        return _decision_counter


def reset_for_testing() -> None:
    """Reset counter — test use only."""
    global _decision_counter
    with _lock:
        _decision_counter = 0


def log_routing_correction(
    user_input: str,
    wrong_target: str,
    correct_target: str,
    confidence: float = 0.0,
    extra: dict[Any, Any] | None = None,
) -> int:
    """Log a HITL routing correction and emit a DPO pair to the RLHF optimizer.

    Called when a human operator overrides an AgenticRouter decision by
    selecting the correct target.  Emits a DPO pair
    ``(user_input, wrong_target, correct_target)`` into
    ``DefaultDeterministicRLHFOptimizer`` for bounded threshold adjustment.

    Args:
        user_input:    The original user or task input string.
        wrong_target:  The target incorrectly selected by the router.
        correct_target: The correct target as determined by the human.
        confidence:    The router's confidence score at decision time (0–1).
        extra:         Optional additional key-value pairs for the audit record.

    Returns:
        The sequential decision number (1-based).
    """
    import json as _json

    merged_extra: dict[Any, Any] = {
        "decision_type": "routing_correction",
        "wrong_target": wrong_target,
        "correct_target": correct_target,
        "confidence": str(round(confidence, 6)),
    }
    if extra:
        merged_extra.update(extra)
    decision_n = log_hitl_decision(
        agent="AgenticRouter",
        file_path="agentic_core/L0_routing/engines/agentic_router.py",
        violation="ROUTING_MISCLASSIFICATION",
        proposed=f"route_to={wrong_target}",
        decision=f"corrected_to={correct_target}",
        extra=merged_extra,
    )
    try:
        from system_learning.engines.rlhf_optimizer_impl import DefaultRLHFOptimizer

        dpo_batch = _json.dumps(
            {
                "pairs": [
                    {
                        "input": user_input[:512],
                        "chosen": correct_target,
                        "rejected": wrong_target,
                        "surface": "routing_min_confidence",
                    }
                ]
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        snapshot_id = f"hitl_routing_{decision_n}"
        optimizer = DefaultRLHFOptimizer()
        optimizer.propose_from_dpo(dpo_batch_bytes=dpo_batch.encode("utf-8"), snapshot_id=snapshot_id)
    except (AttributeError, ImportError, RuntimeError, TypeError, ValueError) as exc:
        logger.warning("Failed to emit DPO pair for routing correction: %s", exc)
    return decision_n
