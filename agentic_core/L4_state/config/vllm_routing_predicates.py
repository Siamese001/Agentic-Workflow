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

from tools.canonical_hash import canonical_hash

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
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
        name="iteration_count_exceeded",
        predicate=iteration_count_exceeded,
        provider=Provider.OPUS,
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
