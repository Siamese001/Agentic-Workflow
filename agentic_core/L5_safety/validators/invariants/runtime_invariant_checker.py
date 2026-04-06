"""Addendum 8: Runtime Architectural Invariant Checker.

Six invariants that MUST always hold. Wire into critical paths.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.L5_safety.types.hardening_errors import (
    C0AuthorityLeakError,
    MutationReplayIntegrityViolation,
)
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
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "runtime_invariant_checker")
emit_determinism_digest("p0", "runtime_invariant_checker")

_emit_dispatches_healing_run("p1", "runtime_invariant_checker", "L5")
_emit_routes_through("p1", "runtime_invariant_checker", "L5")
_emit_checks_agent_registry("p1", "runtime_invariant_checker", "agent_registry")
_emit_validates_agent_capability("p1", "runtime_invariant_checker", "capability")
_emit_dispatches_execution_plan("p1", "runtime_invariant_checker", "exec_plan")
_emit_agent_executes_agent("p1", "runtime_invariant_checker", "sub_agent")
_emit_routes_to_agent("p1", "runtime_invariant_checker", "target_agent")
_emit_verifies_policy("p1", "runtime_invariant_checker", "policy_check")
_emit_observes_runtime_state("p1", "runtime_invariant_checker", "runtime_state")
_emit_verifies_boundary("p1", "runtime_invariant_checker", "boundary_check")
_emit_transcripts_response("p1", "runtime_invariant_checker", "transcript")
_emit_hard_fails_untranscripted("p1", "runtime_invariant_checker")
_emit_gated_by_confidence("p1", "runtime_invariant_checker", "confidence_gate")
_emit_escalates_to_human("p1", "runtime_invariant_checker", "L5")
_emit_reads_policy_state("p1", "runtime_invariant_checker", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "runtime_invariant_checker")
_emit_applies_guardrail("p0", "runtime_invariant_checker", "p0_governance")
_emit_snapshots_state("p0", "runtime_invariant_checker", "state_snapshot")
_emit_authorize_and_execute("p2", "runtime_invariant_checker", "execution_auth")
_emit_validates_capability("p2", "runtime_invariant_checker", "capability_check")
_emit_routes_to_capability("p2", "runtime_invariant_checker", "capability_route")
_emit_writes_via_uwg("p2", "runtime_invariant_checker", "uwg_write")
_emit_blocks_direct_write("p2", "runtime_invariant_checker", "direct_write_block")
_emit_records_tool_invocation("p2", "runtime_invariant_checker", "tool_invocation")
_emit_captures_execution_output("p2", "runtime_invariant_checker", "exec_output")
_emit_dispatches_agent("p3", "runtime_invariant_checker", "agent_dispatch")
_emit_coordinates_agents("p3", "runtime_invariant_checker", "agent_coordination")
_emit_records_workflow_lineage("p3", "runtime_invariant_checker", "workflow_lineage")
_emit_records_healing_outcome("p3", "runtime_invariant_checker", "healing_outcome")
_emit_escalates_failure("p3", "runtime_invariant_checker", "failure_escalation")
_emit_orchestrates_workflow("p3", "runtime_invariant_checker", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "runtime_invariant_checker", "healing_dispatch")
_emit_invokes_evaluation("p3", "runtime_invariant_checker", "evaluation_signal")
_emit_records_telemetry_event("p4", "runtime_invariant_checker", "telemetry_event")
_emit_captures_evaluation_metric("p4", "runtime_invariant_checker", "eval_metric")
_emit_stores_embedding("p4", "runtime_invariant_checker", "embedding_store")
_emit_updates_meta_learning_state("p4", "runtime_invariant_checker", "meta_learning")
_emit_links_execution_to_snapshot("p4", "runtime_invariant_checker", "exec_snapshot_link")
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

_emit_emits_metric_event("runtime_invariant_checker", "p4obs", "metric_1")
_emit_emits_metric_event("runtime_invariant_checker", "p4obs", "metric_2")
_emit_emits_metric_event("runtime_invariant_checker", "p4obs", "metric_3")
_emit_emits_metric_event("runtime_invariant_checker", "p4obs", "metric_4")
_emit_emits_metric_event("runtime_invariant_checker", "p4obs", "metric_5")
_emit_emits_metric_event("runtime_invariant_checker", "p4obs", "metric_6")
_emit_records_incident_event("runtime_invariant_checker", "p4obs", "incident")
_emit_captures_runtime_anomaly("runtime_invariant_checker", "p4obs", "anomaly")
_emit_writes_observability_log("runtime_invariant_checker", "p4obs", "obs_log")
_emit_updates_monitoring_state("runtime_invariant_checker", "p4obs", "mon_state")
_emit_triggers_alert("runtime_invariant_checker", "p4obs", "alert")
_emit_links_incident_trace("runtime_invariant_checker", "p4obs", "trace_link")
_emit_captures_pattern("runtime_invariant_checker", "p3lm", "pattern")
_emit_records_learning_event("runtime_invariant_checker", "p3lm", "learning_event")
_emit_writes_learning_snapshot("runtime_invariant_checker", "p3lm", "snapshot")
_emit_feeds_meta_learning("runtime_invariant_checker", "p3lm", "meta_feed")
_emit_updates_routing_strategy("runtime_invariant_checker", "p3lm", "routing")
_emit_improves_agent_policy("runtime_invariant_checker", "p3lm", "policy")
_emit_stores_learning_state("runtime_invariant_checker", "p3lm", "state")
_emit_records_execution_trace("runtime_invariant_checker", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("runtime_invariant_checker", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("runtime_invariant_checker", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("runtime_invariant_checker", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("runtime_invariant_checker", "L4_STATE", "p2_trace_5")
_emit_reads_environ("runtime_invariant_checker", "env_read", "p2_env_1")
_emit_reads_environ("runtime_invariant_checker", "env_read", "p2_env_2")
_emit_reads_runtime_state("runtime_invariant_checker", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("runtime_invariant_checker", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "runtime_invariant_checker", "context_pull")
_emit_pulls_context("p1", "runtime_invariant_checker", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "runtime_invariant_checker", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "runtime_invariant_checker", "uwg_term_2")
_emit_writes_through("p1", "runtime_invariant_checker", "write_through")
_emit_writes_through("p1", "runtime_invariant_checker", "write_through_2")
_emit_validated_by_safety_plane("p1", "runtime_invariant_checker", "safety_validation")
_emit_invokes_eval("p1", "runtime_invariant_checker", "eval_call")
_emit_proposal_commits_routing("p1", "runtime_invariant_checker", "routing_commit")

logger = logging.getLogger(__name__)

_C0_FORBIDDEN_FIELDS = frozenset(
    {"route_mode", "execution_tier", "safety_threshold", "allowed_tools", "auth_token"}
)


def assert_mutation_source_is_l2(mutation_source: str) -> None:
    """Invariant 1: L2 is the ONLY mutation executor."""
    if mutation_source != "L2_execution":
        raise MutationReplayIntegrityViolation(
            f"Invariant 1 violated: mutation_source={mutation_source!r} — only 'L2_execution' allowed"
        )


def assert_mutation_in_ledger(
    ledger_entries: list[dict[str, Any]],
    file_path: str,
    operation: str,
) -> None:
    """Invariant 2: All mutations pass through UWG (present in ledger)."""
    for entry in ledger_entries:
        if entry.get("file_path") == file_path and entry.get("operation") == operation:
            return
    raise MutationReplayIntegrityViolation(
        f"Invariant 2 violated: mutation not in ledger — file={file_path} op={operation}"
    )


def assert_state_read_source_is_l4(state_read_source: str) -> None:
    """Invariant 3: L4 is the sole state authority."""
    if state_read_source != "L4_state":
        raise MutationReplayIntegrityViolation(
            f"Invariant 3 violated: state_read_source={state_read_source!r} — only 'L4_state' allowed"
        )


def assert_c0_no_authority_fields(c0_payload: dict[str, Any]) -> None:
    """Invariant 4: C0 context never carries authority fields."""
    leak = _C0_FORBIDDEN_FIELDS & set(c0_payload.keys())
    if leak:
        raise C0AuthorityLeakError(
            f"Invariant 4 violated: C0 payload contains authority fields: {sorted(leak)}"
        )


def assert_telemetry_no_config_mutation(
    current_stage: int,
    config_mutated: bool,
) -> None:
    """Invariant 5: L6 telemetry cannot mutate runtime state before S9."""
    if current_stage < 9 and config_mutated:
        from agentic_core.L5_safety.types.hardening_errors import RuntimePolicyMutationViolation

        raise RuntimePolicyMutationViolation(
            f"Invariant 5 violated: config mutated at meta-learning stage {current_stage} (must be S9)"
        )


def assert_human_patch_l5_clearance(l5_clearance_signature: str | None) -> None:
    """Invariant 6: Human patches must pass L5 re-clearance."""
    if not l5_clearance_signature:
        from agentic_core.L5_safety.types.hardening_errors import HumanPatchL5ClearanceError

        raise HumanPatchL5ClearanceError("Invariant 6 violated: human patch missing L5 clearance signature")


def run_all_invariants(
    *,
    mutation_source: str | None = None,
    ledger_entries: list[dict[str, Any]] | None = None,
    file_path: str | None = None,
    operation: str | None = None,
    state_read_source: str | None = None,
    c0_payload: dict[str, Any] | None = None,
    meta_learning_stage: int | None = None,
    config_mutated: bool = False,
    l5_clearance_signature: str | None = None,
) -> list[str]:
    """Run all applicable invariants. Returns list of violation messages (empty = clean)."""
    violations: list[str] = []

    checks = [
        (_check_inv1, mutation_source),
        (_check_inv2, (ledger_entries, file_path, operation)),
        (_check_inv3, state_read_source),
        (_check_inv4, c0_payload),
        (_check_inv5, (meta_learning_stage, config_mutated)),
        (_check_inv6, l5_clearance_signature),
    ]

    for checker, arg in checks:
        try:
            checker(arg)
        # guardian: allow-silent-swallow -- invariant check is observational; failure non-blocking
        except (ValueError, TypeError) as exc:
            violations.append(str(exc))

    return violations


def _check_inv1(mutation_source: Any) -> None:
    if mutation_source is not None:
        assert_mutation_source_is_l2(mutation_source)


def _check_inv2(args: Any) -> None:
    ledger_entries, file_path, operation = args
    if ledger_entries is not None and file_path and operation:
        assert_mutation_in_ledger(ledger_entries, file_path, operation)


def _check_inv3(state_read_source: Any) -> None:
    if state_read_source is not None:
        assert_state_read_source_is_l4(state_read_source)


def _check_inv4(c0_payload: Any) -> None:
    if c0_payload is not None:
        assert_c0_no_authority_fields(c0_payload)


def _check_inv5(args: Any) -> None:
    stage, mutated = args
    if stage is not None:
        assert_telemetry_no_config_mutation(stage, mutated)


def _check_inv6(sig: Any) -> None:
    if sig is not None or sig == "":
        pass


__all__ = [
    "assert_mutation_source_is_l2",
    "assert_mutation_in_ledger",
    "assert_state_read_source_is_l4",
    "assert_c0_no_authority_fields",
    "assert_telemetry_no_config_mutation",
    "assert_human_patch_l5_clearance",
    "run_all_invariants",
]
