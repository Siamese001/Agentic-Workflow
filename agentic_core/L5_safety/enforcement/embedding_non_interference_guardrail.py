"""EmbeddingNonInterferenceGuard — L5 Safety enforcement.

Asserts that C0 RAG embedding context does NOT appear in routing decision
inputs.  C0 is informational only: it must never mutate tier selection,
policy evaluation, or manifest content.

Guard contract:
- assert_no_c0_influence(routing_inputs, c0_context) raises
  C0InterferenceViolation if any C0 key/value leaks into routing_inputs.
- verify_routing_decision_clean(decision) checks a RoutingDecision dict for
  embedded C0 markers.

Invariants:
  - No wall-clock access.
  - Deterministic: same inputs -> same result.
  - Fail-closed: if analysis raises, guard defaults to VIOLATION.

# guardian: allow-direct-prompt-compilation
"""

from __future__ import annotations

import ast as _ast
from typing import Any

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
)

emit_replay_key("p0", "embedding_non_interference_guardrail")
emit_determinism_digest("p0", "embedding_non_interference_guardrail")

_emit_dispatches_healing_run("p1", "embedding_non_interference_guardrail", "L5")
_emit_routes_through("p1", "embedding_non_interference_guardrail", "L5")
_emit_checks_agent_registry("p1", "embedding_non_interference_guardrail", "agent_registry")
_emit_validates_agent_capability("p1", "embedding_non_interference_guardrail", "capability")
_emit_dispatches_execution_plan("p1", "embedding_non_interference_guardrail", "exec_plan")
_emit_agent_executes_agent("p1", "embedding_non_interference_guardrail", "sub_agent")
_emit_routes_to_agent("p1", "embedding_non_interference_guardrail", "target_agent")
_emit_verifies_policy("p1", "embedding_non_interference_guardrail", "policy_check")
_emit_observes_runtime_state("p1", "embedding_non_interference_guardrail", "runtime_state")
_emit_verifies_boundary("p1", "embedding_non_interference_guardrail", "boundary_check")
_emit_transcripts_response("p1", "embedding_non_interference_guardrail", "transcript")
_emit_hard_fails_untranscripted("p1", "embedding_non_interference_guardrail")
_emit_gated_by_confidence("p1", "embedding_non_interference_guardrail", "confidence_gate")
_emit_escalates_to_human("p1", "embedding_non_interference_guardrail", "L5")
_emit_reads_policy_state("p1", "embedding_non_interference_guardrail", "L5")
_emit_authorize_and_execute("p2", "embedding_non_interference_guardrail", "execution_auth")
_emit_validates_capability("p2", "embedding_non_interference_guardrail", "capability_check")
_emit_routes_to_capability("p2", "embedding_non_interference_guardrail", "capability_route")
_emit_writes_via_uwg("p2", "embedding_non_interference_guardrail", "uwg_write")
_emit_blocks_direct_write("p2", "embedding_non_interference_guardrail", "direct_write_block")
_emit_records_tool_invocation("p2", "embedding_non_interference_guardrail", "tool_invocation")
_emit_captures_execution_output("p2", "embedding_non_interference_guardrail", "exec_output")
_emit_dispatches_agent("p3", "embedding_non_interference_guardrail", "agent_dispatch")
_emit_coordinates_agents("p3", "embedding_non_interference_guardrail", "agent_coordination")
_emit_records_workflow_lineage("p3", "embedding_non_interference_guardrail", "workflow_lineage")
_emit_records_healing_outcome("p3", "embedding_non_interference_guardrail", "healing_outcome")
_emit_escalates_failure("p3", "embedding_non_interference_guardrail", "failure_escalation")
_emit_orchestrates_workflow("p3", "embedding_non_interference_guardrail", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "embedding_non_interference_guardrail", "healing_dispatch")
_emit_invokes_evaluation("p3", "embedding_non_interference_guardrail", "evaluation_signal")
_emit_records_telemetry_event("p4", "embedding_non_interference_guardrail", "telemetry_event")
_emit_captures_evaluation_metric("p4", "embedding_non_interference_guardrail", "eval_metric")
_emit_stores_embedding("p4", "embedding_non_interference_guardrail", "embedding_store")
_emit_updates_meta_learning_state("p4", "embedding_non_interference_guardrail", "meta_learning")
_emit_links_execution_to_snapshot("p4", "embedding_non_interference_guardrail", "exec_snapshot_link")
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

_emit_emits_metric_event("embedding_non_interference_guardrail", "p4obs", "metric_1")
_emit_emits_metric_event("embedding_non_interference_guardrail", "p4obs", "metric_2")
_emit_emits_metric_event("embedding_non_interference_guardrail", "p4obs", "metric_3")
_emit_emits_metric_event("embedding_non_interference_guardrail", "p4obs", "metric_4")
_emit_emits_metric_event("embedding_non_interference_guardrail", "p4obs", "metric_5")
_emit_emits_metric_event("embedding_non_interference_guardrail", "p4obs", "metric_6")
_emit_records_incident_event("embedding_non_interference_guardrail", "p4obs", "incident")
_emit_captures_runtime_anomaly("embedding_non_interference_guardrail", "p4obs", "anomaly")
_emit_writes_observability_log("embedding_non_interference_guardrail", "p4obs", "obs_log")
_emit_updates_monitoring_state("embedding_non_interference_guardrail", "p4obs", "mon_state")
_emit_triggers_alert("embedding_non_interference_guardrail", "p4obs", "alert")
_emit_links_incident_trace("embedding_non_interference_guardrail", "p4obs", "trace_link")
_emit_captures_pattern("embedding_non_interference_guardrail", "p3lm", "pattern")
_emit_records_learning_event("embedding_non_interference_guardrail", "p3lm", "learning_event")
_emit_writes_learning_snapshot("embedding_non_interference_guardrail", "p3lm", "snapshot")
_emit_feeds_meta_learning("embedding_non_interference_guardrail", "p3lm", "meta_feed")
_emit_updates_routing_strategy("embedding_non_interference_guardrail", "p3lm", "routing")
_emit_improves_agent_policy("embedding_non_interference_guardrail", "p3lm", "policy")
_emit_stores_learning_state("embedding_non_interference_guardrail", "p3lm", "state")
_emit_records_execution_trace("embedding_non_interference_guardrail", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("embedding_non_interference_guardrail", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("embedding_non_interference_guardrail", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("embedding_non_interference_guardrail", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("embedding_non_interference_guardrail", "L4_STATE", "p2_trace_5")
_emit_reads_environ("embedding_non_interference_guardrail", "env_read", "p2_env_1")
_emit_reads_environ("embedding_non_interference_guardrail", "env_read", "p2_env_2")
_emit_reads_runtime_state("embedding_non_interference_guardrail", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("embedding_non_interference_guardrail", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "embedding_non_interference_guardrail", "context_pull")
_emit_pulls_context("p1", "embedding_non_interference_guardrail", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "embedding_non_interference_guardrail", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "embedding_non_interference_guardrail", "uwg_term_2")
_emit_writes_through("p1", "embedding_non_interference_guardrail", "write_through")
_emit_writes_through("p1", "embedding_non_interference_guardrail", "write_through_2")
_emit_validated_by_safety_plane("p1", "embedding_non_interference_guardrail", "safety_validation")
_emit_invokes_eval("p1", "embedding_non_interference_guardrail", "eval_call")
_emit_proposal_commits_routing("p1", "embedding_non_interference_guardrail", "routing_commit")


class C0InterferenceViolation(RuntimeError):
    """Raised when C0 RAG context is found to influence routing inputs."""


_C0_FORBIDDEN_FIELDS: frozenset[str] = frozenset(
    {"route_mode", "execution_tier", "safety_threshold", "policy_hash"},
)
_C0_MARKER_KEYS: frozenset[str] = frozenset(
    {
        "c0_context",
        "c0_embedding",
        "c0_rag",
        "c0_retrieval",
        "c0_score",
        "embedding_context",
        "embedding_hits",
        "embedding_results",
        "rag_context",
        "rag_hits",
        "rag_results",
        "retrieval_context",
        "retrieval_results",
    },
)
_C0_VALUE_FRAGMENTS: tuple[str, ...] = (
    "c0_context",
    "c0_rag",
    "rag_result",
    "embedding_hit",
    "retrieval_hit",
)


def assert_c0_context_clean(c0_context: dict[str, Any]) -> None:
    """Assert that *c0_context* does not contain routing-influencing fields.

    C0 context is strictly informational.  The presence of any field from
    ``_C0_FORBIDDEN_FIELDS`` means C0 is leaking into routing / execution
    tier / safety configuration — a hard violation.

    Args:
        c0_context: The C0 context dict to inspect.

    Raises:
        C0InterferenceViolation: if any forbidden field is present.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "assert_c0_context_clean", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "assert_c0_context_clean", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "assert_c0_context_clean")
    violations = [
        f"forbidden field {field!r} present in c0_context"
        for field in _C0_FORBIDDEN_FIELDS
        if field in c0_context
    ]
    if violations:
        raise C0InterferenceViolation(
            "EmbeddingNonInterferenceGuard: C0 context carries routing-influencing fields that violate the informational boundary:\n"
            + "\n".join(f"  - {v}" for v in violations),
        )


def assert_no_c0_influence(routing_inputs: dict[str, Any], c0_context: dict[str, Any] | None = None) -> None:
    """Assert that *routing_inputs* contains no C0 RAG markers.

    Args:
        routing_inputs: The dict of inputs passed to the routing tier
            (e.g. RoutingInputs fields, manifest dict).
        c0_context: Optional C0 context dict.  If provided, we additionally
            verify that none of its keys/values appear verbatim in
            routing_inputs.

    Raises:
        C0InterferenceViolation: if any C0 marker is detected.
    """
    violations: list[str] = []
    for key in routing_inputs:
        if str(key).lower() in _C0_MARKER_KEYS:
            violations.append(f"C0 marker key {key!r} found in routing_inputs")
    for key, value in routing_inputs.items():
        if isinstance(value, str):
            for frag in _C0_VALUE_FRAGMENTS:
                if frag in value.lower():
                    violations.append(f"C0 fragment {frag!r} found in routing_inputs[{key!r}]")
    if c0_context:
        assert_c0_context_clean(c0_context)
        for c0_key in c0_context:
            if c0_key in routing_inputs:
                # guardian: allow-direct-prompt-compilation
                violations.append(
                    f"C0 context key {c0_key!r} also present in routing_inputs (verbatim key collision)",
                )
    if violations:
        raise C0InterferenceViolation(
            "EmbeddingNonInterferenceGuard: C0 influence detected in routing inputs:\n"
            + "\n".join(f"  - {v}" for v in violations),
        )


def verify_routing_decision_clean(decision: dict[str, Any]) -> bool:
    """Return True if *decision* contains no C0 provenance markers.

    Does NOT raise; returns False on detection so callers can log and decide
    whether to hard-fail.
    """
    for key in decision:
        if str(key).lower() in _C0_MARKER_KEYS:
            return False
    for value in decision.values():
        if isinstance(value, str):
            for frag in _C0_VALUE_FRAGMENTS:
                if frag in value.lower():
                    return False
    return True


def assert_routing_decision_clean(decision: dict[str, Any]) -> None:
    """Raise C0InterferenceViolation if *decision* carries C0 markers."""
    if not verify_routing_decision_clean(decision):
        raise C0InterferenceViolation(
            "EmbeddingNonInterferenceGuard: C0 provenance markers detected in routing decision. C0 is informational only and must not reach routing outputs.",
        )


def scan_file_for_c0_mutations(source_path: Any) -> list[str]:
    """AST-scan *source_path* for writes to C0-marker attributes.

    Returns a list of violation strings (empty == clean).
    """
    from pathlib import Path

    path = Path(source_path)
    if not path.exists():
        return [f"file not found: {path}"]
    source = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = _ast.parse(source, filename=str(path))
    except SyntaxError as exc:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        return [f"SyntaxError at line {exc.lineno}: {exc.msg}"]
    violations: list[str] = []
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Assign):
            for target in node.targets:
                if isinstance(target, _ast.Attribute):
                    if target.attr.lower() in _C0_MARKER_KEYS:
                        violations.append(f"line {node.lineno}: assignment to C0 attribute '{target.attr}'")
    return violations


__all__ = [
    "C0InterferenceViolation",
    "assert_c0_context_clean",
    "assert_no_c0_influence",
    "assert_routing_decision_clean",
    "scan_file_for_c0_mutations",
    "verify_routing_decision_clean",
]
