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

from tools.canonical_hash import canonical_hash

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
