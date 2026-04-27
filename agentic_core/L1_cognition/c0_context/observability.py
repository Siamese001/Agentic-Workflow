"""C0.7 PHASE 3 — OTEL span-tree contract for the C0 Context Engine.

Doctrine: ``docs/reference/03A_C0_Context_Engine/C0.7_C0_Observability_Tests_Anti_Bypass.md``

C0.7 mandates a parent ``c0.stage`` span with a deterministic child-span tree
(``c0.0.preflight`` … ``c0.6.refinement``) and a fixed set of mandatory
attributes on the parent. This module is the canonical emitter — every C0
runtime should call ``emit_c0_stage_span(...)`` exactly once per invocation.

Design notes (additive — no edits to ``preflight``, ``shape_and_scan``,
``contract``, ``refine``):
  * Pure dataclass + emitter pattern. Stage modules build a
    :class:`C0SpanTree` describing what they did, then hand it to the
    emitter, which serialises to whatever tracer the host wires in.
  * Replay-deterministic: the same :class:`C0SpanTree` produces the same
    aggregate digest. Tests rely on this property.
  * Tracer-agnostic: a thin :class:`C0Tracer` protocol lets the host inject
    OpenTelemetry, no-op, or in-memory recorders without changing C0 code.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Final, Protocol


C0_PARENT_SPAN_NAME: Final[str] = "c0.stage"

C0_CHILD_SPAN_NAMES: Final[tuple[str, ...]] = (
    "c0.0.preflight",
    "c0.1.retrieval_plan",
    "c0.2.evidence_fetch",
    "c0.2.lane.dense",
    "c0.2.lane.sparse",
    "c0.2.lane.metadata",
    "c0.2.lane.cache",
    "c0.2.lane.trace",
    "c0.2.lane.code",
    "c0.2.hydration",
    "c0.3.graph_traverse",
    "c0.4.shape_rerank_stratify",
    "c0.5.evidence_contract",
    "c0.6.refinement",
)

C0_PARENT_REQUIRED_ATTRS: Final[frozenset[str]] = frozenset(
    {
        "run_id",
        "request_id",
        "trace_id",
        "route_id",
        "evidence_status",
        "support_score",
        "contradiction_count",
        "unresolved_gap_count",
        "refine_attempts_used",
        "evidence_contract_hash",
        "preflight_manifest_hash",
        "plan_manifest_hash",
        "pool_manifest_hash",
        "shaped_set_hash",
        "recommended_disposition",
    }
)

C0_STAGE_TO_SPAN: Final[dict[str, str]] = {
    "C0.0": "c0.0.preflight",
    "C0.1": "c0.1.retrieval_plan",
    "C0.2": "c0.2.evidence_fetch",
    "C0.2A": "c0.2.hydration",
    "C0.3": "c0.3.graph_traverse",
    "C0.4": "c0.4.shape_rerank_stratify",
    "C0.5": "c0.5.evidence_contract",
    "C0.6": "c0.6.refinement",
}


class SpanContractError(RuntimeError):
    """Raised when a span tree violates the C0.7 PHASE 3 contract."""


@dataclass(frozen=True)
class C0SpanEvent:
    name: str
    reason_code: str
    severity: str = "info"
    attributes: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class C0ChildSpan:
    name: str
    invoked: bool
    duration_ms: int = 0
    events: tuple[C0SpanEvent, ...] = ()
    attributes: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class C0SpanTree:
    parent_attributes: dict[str, Any]
    children: tuple[C0ChildSpan, ...]

    def child_names(self) -> tuple[str, ...]:
        return tuple(c.name for c in self.children)

    def invoked_child_names(self) -> tuple[str, ...]:
        return tuple(c.name for c in self.children if c.invoked)


class C0Tracer(Protocol):
    def start_parent(self, name: str, attributes: dict[str, Any]) -> None: ...

    def add_child(self, child: C0ChildSpan) -> None: ...

    def end_parent(self) -> None: ...


@dataclass
class InMemoryTracer:
    parent_name: str = ""
    parent_attributes: dict[str, Any] = field(default_factory=dict)
    child_records: list[C0ChildSpan] = field(default_factory=list)
    closed: bool = False

    def start_parent(self, name: str, attributes: dict[str, Any]) -> None:
        self.parent_name = name
        self.parent_attributes = dict(attributes)
        self.child_records = []
        self.closed = False

    def add_child(self, child: C0ChildSpan) -> None:
        self.child_records.append(child)

    def end_parent(self) -> None:
        self.closed = True


def validate_span_tree(tree: C0SpanTree) -> None:
    """Enforce C0.7 §PHASE 3 contract."""
    missing = C0_PARENT_REQUIRED_ATTRS - set(tree.parent_attributes.keys())
    if missing:
        raise SpanContractError(
            f"c0.stage span missing required attributes: {sorted(missing)}",
        )
    canonical = set(C0_CHILD_SPAN_NAMES)
    for c in tree.children:
        if c.name not in canonical:
            raise SpanContractError(
                f"unknown child span name {c.name!r}; must be one of {sorted(canonical)}",
            )
    seen: set[str] = set()
    for c in tree.children:
        if c.name in seen:
            raise SpanContractError(f"duplicate child span: {c.name!r}")
        seen.add(c.name)
    canonical_order = list(C0_CHILD_SPAN_NAMES)
    last_idx = -1
    for c in tree.children:
        idx = canonical_order.index(c.name)
        if idx < last_idx:
            raise SpanContractError(
                f"child {c.name!r} appears out of canonical order",
            )
        last_idx = idx
    REQUIRED_ALWAYS = {
        "c0.0.preflight",
        "c0.1.retrieval_plan",
        "c0.2.evidence_fetch",
        "c0.2.hydration",
        "c0.3.graph_traverse",
        "c0.4.shape_rerank_stratify",
        "c0.5.evidence_contract",
    }
    present_names = {c.name for c in tree.children}
    missing_required = REQUIRED_ALWAYS - present_names
    if missing_required:
        raise SpanContractError(
            f"required stages silently omitted (must appear with invoked=False if not run): "
            f"{sorted(missing_required)}",
        )
    rd = tree.parent_attributes.get("recommended_disposition", "")
    valid_dispositions = {
        "proceed",
        "proceed_with_caveat",
        "abstain",
        "fallback_R5",
        "reroute",
        "human_review",
    }
    if rd not in valid_dispositions:
        raise SpanContractError(
            f"recommended_disposition={rd!r} is not a valid C0 disposition; "
            f"must be one of {sorted(valid_dispositions)}",
        )
    FORBIDDEN_TOKENS = {
        "ALLOW",
        "DENY",
        "ESCALATE_HITL",
        "COMMIT_REQUEST",
        "BLOCK_COMMIT",
        "ALLOW_FINISH",
        "QUARANTINE",
    }
    for k, v in tree.parent_attributes.items():
        if isinstance(v, str) and v in FORBIDDEN_TOKENS:
            raise SpanContractError(
                f"forbidden runtime-disposition token {v!r} in parent attribute {k!r}",
            )
    for c in tree.children:
        for ev in c.events:
            if ev.reason_code in FORBIDDEN_TOKENS:
                raise SpanContractError(
                    f"forbidden runtime-disposition token {ev.reason_code!r} "
                    f"in child {c.name!r} event {ev.name!r}",
                )


def emit_c0_stage_span(tree: C0SpanTree, tracer: C0Tracer) -> None:
    validate_span_tree(tree)
    tracer.start_parent(C0_PARENT_SPAN_NAME, tree.parent_attributes)
    for child in tree.children:
        tracer.add_child(child)
    tracer.end_parent()


def aggregate_span_tree_hash(tree: C0SpanTree) -> str:
    payload = {
        "parent": dict(sorted(tree.parent_attributes.items())),
        "children": [
            {
                "name": c.name,
                "invoked": c.invoked,
                "duration_ms": c.duration_ms,
                "events": [
                    {
                        "name": ev.name,
                        "reason_code": ev.reason_code,
                        "severity": ev.severity,
                        "attributes": list(ev.attributes),
                    }
                    for ev in c.events
                ],
                "attributes": list(c.attributes),
            }
            for c in tree.children
        ],
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(),
    ).hexdigest()[:32]


def build_default_span_tree(
    *,
    run_id: str,
    request_id: str,
    trace_id: str,
    route_id: str,
    evidence_status: str,
    support_score: float,
    contradiction_count: int,
    unresolved_gap_count: int,
    refine_attempts_used: int,
    evidence_contract_hash: str,
    preflight_manifest_hash: str,
    plan_manifest_hash: str,
    pool_manifest_hash: str,
    shaped_set_hash: str,
    recommended_disposition: str,
    refinement_invoked: bool = False,
    extra_lanes_invoked: tuple[str, ...] = ("dense", "sparse"),
) -> C0SpanTree:
    parent_attrs: dict[str, Any] = {
        "run_id": run_id,
        "request_id": request_id,
        "trace_id": trace_id,
        "route_id": route_id,
        "evidence_status": evidence_status,
        "support_score": round(support_score, 6),
        "contradiction_count": contradiction_count,
        "unresolved_gap_count": unresolved_gap_count,
        "refine_attempts_used": refine_attempts_used,
        "evidence_contract_hash": evidence_contract_hash,
        "preflight_manifest_hash": preflight_manifest_hash,
        "plan_manifest_hash": plan_manifest_hash,
        "pool_manifest_hash": pool_manifest_hash,
        "shaped_set_hash": shaped_set_hash,
        "recommended_disposition": recommended_disposition,
    }
    invoked_lanes = set(extra_lanes_invoked)
    children: list[C0ChildSpan] = []
    for name in C0_CHILD_SPAN_NAMES:
        if name == "c0.6.refinement":
            children.append(C0ChildSpan(name=name, invoked=refinement_invoked))
        elif name.startswith("c0.2.lane."):
            lane = name.rsplit(".", 1)[-1]
            children.append(C0ChildSpan(name=name, invoked=lane in invoked_lanes))
        else:
            children.append(C0ChildSpan(name=name, invoked=True))
    return C0SpanTree(parent_attributes=parent_attrs, children=tuple(children))


__all__ = [
    "C0_CHILD_SPAN_NAMES",
    "C0_PARENT_REQUIRED_ATTRS",
    "C0_PARENT_SPAN_NAME",
    "C0_STAGE_TO_SPAN",
    "C0ChildSpan",
    "C0SpanEvent",
    "C0SpanTree",
    "C0Tracer",
    "InMemoryTracer",
    "SpanContractError",
    "aggregate_span_tree_hash",
    "build_default_span_tree",
    "emit_c0_stage_span",
    "validate_span_tree",
]
