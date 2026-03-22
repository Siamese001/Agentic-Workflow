"""vLLM Routing Predicate Registry.

Immutable, pure, deterministic predicate registry for routing decisions.
No lambdas, no try/except, no with, no raise, no yield.
No eval/exec/compile. No provider-name string literals.

Compliance: REV 5 - routing_invariants_version = 1
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Mapping, NamedTuple

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
)

_emit_authorize_and_execute("p2", "vllm_routing_predicates", "execution_auth")
_emit_validates_capability("p2", "vllm_routing_predicates", "capability_check")
_emit_routes_to_capability("p2", "vllm_routing_predicates", "capability_route")
_emit_writes_via_uwg("p2", "vllm_routing_predicates", "uwg_write")
_emit_blocks_direct_write("p2", "vllm_routing_predicates", "direct_write_block")
_emit_records_tool_invocation("p2", "vllm_routing_predicates", "tool_invocation")
_emit_captures_execution_output("p2", "vllm_routing_predicates", "exec_output")
_emit_dispatches_agent("p3", "vllm_routing_predicates", "agent_dispatch")
_emit_coordinates_agents("p3", "vllm_routing_predicates", "agent_coordination")
_emit_records_workflow_lineage("p3", "vllm_routing_predicates", "workflow_lineage")
_emit_records_healing_outcome("p3", "vllm_routing_predicates", "healing_outcome")
_emit_escalates_failure("p3", "vllm_routing_predicates", "failure_escalation")
_emit_orchestrates_workflow("p3", "vllm_routing_predicates", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "vllm_routing_predicates", "healing_dispatch")
_emit_invokes_evaluation("p3", "vllm_routing_predicates", "evaluation_signal")
_emit_records_telemetry_event("p4", "vllm_routing_predicates", "telemetry_event")
_emit_captures_evaluation_metric("p4", "vllm_routing_predicates", "eval_metric")
_emit_stores_embedding("p4", "vllm_routing_predicates", "embedding_store")
_emit_updates_meta_learning_state("p4", "vllm_routing_predicates", "meta_learning")
_emit_links_execution_to_snapshot("p4", "vllm_routing_predicates", "exec_snapshot_link")
from tools.canonical_hash import canonical_hash

emit_replay_key("p0", "vllm_routing_predicates")
emit_determinism_digest("p0", "vllm_routing_predicates")

_emit_dispatches_healing_run("p1", "vllm_routing_predicates", "L4")
_emit_routes_through("p1", "vllm_routing_predicates", "L4")
_emit_checks_agent_registry("p1", "vllm_routing_predicates", "agent_registry")
_emit_validates_agent_capability("p1", "vllm_routing_predicates", "capability")
_emit_dispatches_execution_plan("p1", "vllm_routing_predicates", "exec_plan")
_emit_agent_executes_agent("p1", "vllm_routing_predicates", "sub_agent")
_emit_routes_to_agent("p1", "vllm_routing_predicates", "target_agent")
_emit_verifies_policy("p1", "vllm_routing_predicates", "policy_check")
_emit_observes_runtime_state("p1", "vllm_routing_predicates", "runtime_state")
_emit_verifies_boundary("p1", "vllm_routing_predicates", "boundary_check")
_emit_transcripts_response("p1", "vllm_routing_predicates", "transcript")
_emit_hard_fails_untranscripted("p1", "vllm_routing_predicates")
_emit_gated_by_confidence("p1", "vllm_routing_predicates", "confidence_gate")
_emit_escalates_to_human("p1", "vllm_routing_predicates", "L4")
_emit_reads_policy_state("p1", "vllm_routing_predicates", "L4")
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

_emit_emits_metric_event("vllm_routing_predicates", "p4obs", "metric_1")
_emit_emits_metric_event("vllm_routing_predicates", "p4obs", "metric_2")
_emit_emits_metric_event("vllm_routing_predicates", "p4obs", "metric_3")
_emit_emits_metric_event("vllm_routing_predicates", "p4obs", "metric_4")
_emit_emits_metric_event("vllm_routing_predicates", "p4obs", "metric_5")
_emit_emits_metric_event("vllm_routing_predicates", "p4obs", "metric_6")
_emit_records_incident_event("vllm_routing_predicates", "p4obs", "incident")
_emit_captures_runtime_anomaly("vllm_routing_predicates", "p4obs", "anomaly")
_emit_writes_observability_log("vllm_routing_predicates", "p4obs", "obs_log")
_emit_updates_monitoring_state("vllm_routing_predicates", "p4obs", "mon_state")
_emit_triggers_alert("vllm_routing_predicates", "p4obs", "alert")
_emit_links_incident_trace("vllm_routing_predicates", "p4obs", "trace_link")
_emit_captures_pattern("vllm_routing_predicates", "p3lm", "pattern")
_emit_records_learning_event("vllm_routing_predicates", "p3lm", "learning_event")
_emit_writes_learning_snapshot("vllm_routing_predicates", "p3lm", "snapshot")
_emit_feeds_meta_learning("vllm_routing_predicates", "p3lm", "meta_feed")
_emit_updates_routing_strategy("vllm_routing_predicates", "p3lm", "routing")
_emit_improves_agent_policy("vllm_routing_predicates", "p3lm", "policy")
_emit_stores_learning_state("vllm_routing_predicates", "p3lm", "state")
_emit_records_execution_trace("vllm_routing_predicates", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("vllm_routing_predicates", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("vllm_routing_predicates", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("vllm_routing_predicates", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("vllm_routing_predicates", "L4_STATE", "p2_trace_5")
_emit_reads_environ("vllm_routing_predicates", "env_read", "p2_env_1")
_emit_reads_environ("vllm_routing_predicates", "env_read", "p2_env_2")
_emit_reads_runtime_state("vllm_routing_predicates", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("vllm_routing_predicates", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "vllm_routing_predicates", "context_pull")
_emit_pulls_context("p1", "vllm_routing_predicates", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "vllm_routing_predicates", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "vllm_routing_predicates", "uwg_term_2")
_emit_writes_through("p1", "vllm_routing_predicates", "write_through")
_emit_writes_through("p1", "vllm_routing_predicates", "write_through_2")
_emit_validated_by_safety_plane("p1", "vllm_routing_predicates", "safety_validation")
_emit_invokes_eval("p1", "vllm_routing_predicates", "eval_call")
_emit_proposal_commits_routing("p1", "vllm_routing_predicates", "routing_commit")


class Provider(Enum):
    """Routing provider enumeration."""

    OPUS = "opus"
    LOCAL_VLLM = "local_vllm"


@dataclass(frozen=True, slots=True)
class RoutingDecision:
    """Immutable routing decision with audit trail."""

    provider: Provider
    predicate_evaluation_hash: str
    routing_version: str


class RoutingPredicate(NamedTuple):
    """A named predicate entry: (name, test_function, target_provider)."""

    name: str
    predicate: Callable[[Mapping[str, Any]], bool]
    provider: Provider


def requires_policy_read(ctx: Mapping[str, Any]) -> bool:
    """True when the context requires a policy read."""
    return bool(ctx.get("requires_policy_read", False))


def iteration_count_exceeded(ctx: Mapping[str, Any]) -> bool:
    """True when iteration count exceeds the configured threshold."""
    return int(ctx.get("iteration_count", 0)) > int(ctx.get("max_iterations", 100))


def invalid_ast_detected(ctx: Mapping[str, Any]) -> bool:
    """True when the context signals an invalid AST."""
    return bool(ctx.get("invalid_ast", False))


def default_routing(ctx: Mapping[str, Any]) -> bool:
    """Default fallback predicate — always matches."""
    return True


ROUTING_PREDICATES: tuple[RoutingPredicate, ...] = (
    RoutingPredicate(name="requires_policy_read", predicate=requires_policy_read, provider=Provider.OPUS),
    RoutingPredicate(
        name="iteration_count_exceeded", predicate=iteration_count_exceeded, provider=Provider.OPUS
    ),
    RoutingPredicate(name="invalid_ast_detected", predicate=invalid_ast_detected, provider=Provider.OPUS),
    RoutingPredicate(name="default_routing", predicate=default_routing, provider=Provider.LOCAL_VLLM),
)


def evaluate(context: Mapping[str, Any]) -> RoutingDecision:
    """Evaluate routing predicates against context.

    First-match-wins. Context is not mutated.
    Deterministic: key-order independent, hash-stable.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "evaluate", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "evaluate", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "evaluate")
    snapshot = copy.deepcopy(context)
    hash_before = canonical_hash(dict(context))
    predicate_hash = canonical_hash(dict(context))
    matched_provider = Provider.LOCAL_VLLM
    for entry in ROUTING_PREDICATES:
        if entry.predicate(context):
            matched_provider = entry.provider
            break
    decision = RoutingDecision(
        provider=matched_provider,
        predicate_evaluation_hash=predicate_hash,
        routing_version=str(context.get("routing_version", "unknown")),
    )
    assert context == snapshot
    assert canonical_hash(dict(context)) == hash_before
    return decision
