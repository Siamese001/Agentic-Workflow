"""C0.7 PHASE 3 OTEL span-tree contract tests.

Doctrine: ``docs/reference/03A_C0_Context_Engine/C0.7_C0_Observability_Tests_Anti_Bypass.md``

Verifies the additive ``observability`` module emits a contract-conformant
parent ``c0.stage`` span, every required child span (with explicit
``invoked=False`` for absent stages), every mandatory parent attribute, and
a replay-stable aggregate hash.
"""

from __future__ import annotations

import pytest

from agentic_core.L1_cognition.c0_context.observability import (
    C0_CHILD_SPAN_NAMES,
    C0_PARENT_REQUIRED_ATTRS,
    C0_PARENT_SPAN_NAME,
    C0ChildSpan,
    C0SpanEvent,
    C0SpanTree,
    InMemoryTracer,
    SpanContractError,
    aggregate_span_tree_hash,
    build_default_span_tree,
    emit_c0_stage_span,
    validate_span_tree,
)


def _default_attrs(**overrides) -> dict:
    base = {
        "run_id": "run-1",
        "request_id": "req-1",
        "trace_id": "trace-1",
        "route_id": "R3_GROUNDED",
        "evidence_status": "PASS",
        "support_score": 0.82,
        "contradiction_count": 0,
        "unresolved_gap_count": 0,
        "refine_attempts_used": 0,
        "evidence_contract_hash": "h-c",
        "preflight_manifest_hash": "h-pf",
        "plan_manifest_hash": "h-plan",
        "pool_manifest_hash": "h-pool",
        "shaped_set_hash": "h-shaped",
        "recommended_disposition": "proceed",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Span-name vocabulary contract.
# ---------------------------------------------------------------------------


def test_parent_span_name_is_c0_stage() -> None:
    assert C0_PARENT_SPAN_NAME == "c0.stage"


def test_child_span_names_match_spec_exactly() -> None:
    expected = (
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
    assert C0_CHILD_SPAN_NAMES == expected


def test_required_parent_attrs_match_spec_count_fifteen() -> None:
    # C0.7 §PHASE 3 enumerates 15 mandatory attributes on c0.stage.
    assert len(C0_PARENT_REQUIRED_ATTRS) == 15


# ---------------------------------------------------------------------------
# Validation contract.
# ---------------------------------------------------------------------------


def test_validate_default_tree_passes() -> None:
    tree = build_default_span_tree(**_default_attrs())  # type: ignore[arg-type]
    validate_span_tree(tree)


def test_validate_rejects_missing_parent_attribute() -> None:
    attrs = _default_attrs()
    del attrs["evidence_contract_hash"]
    tree = C0SpanTree(parent_attributes=attrs, children=())
    with pytest.raises(SpanContractError, match="missing required attributes"):
        validate_span_tree(tree)


def test_validate_rejects_unknown_child_name() -> None:
    bogus = C0ChildSpan(name="c0.99.unknown", invoked=True)
    # Default attrs satisfy parent reqs; child is the offender.
    tree = C0SpanTree(parent_attributes=_default_attrs(), children=(bogus,))
    with pytest.raises(SpanContractError, match="unknown child span name"):
        validate_span_tree(tree)


def test_validate_rejects_duplicate_child() -> None:
    twice = C0ChildSpan(name="c0.0.preflight", invoked=True)
    tree = C0SpanTree(
        parent_attributes=_default_attrs(),
        children=(twice, twice),
    )
    with pytest.raises(SpanContractError, match="duplicate child span"):
        validate_span_tree(tree)


def test_validate_rejects_out_of_order_children() -> None:
    out_of_order = (
        C0ChildSpan(name="c0.5.evidence_contract", invoked=True),
        C0ChildSpan(name="c0.0.preflight", invoked=True),
    )
    tree = C0SpanTree(parent_attributes=_default_attrs(), children=out_of_order)
    with pytest.raises(SpanContractError, match="out of canonical order"):
        validate_span_tree(tree)


def test_validate_requires_explicit_absent_stages_no_silent_omission() -> None:
    # Build a tree that has only c0.0 and c0.1 — the others are silently absent.
    tree = C0SpanTree(
        parent_attributes=_default_attrs(),
        children=(
            C0ChildSpan(name="c0.0.preflight", invoked=True),
            C0ChildSpan(name="c0.1.retrieval_plan", invoked=True),
        ),
    )
    with pytest.raises(SpanContractError, match="silently omitted"):
        validate_span_tree(tree)


def test_validate_rejects_invalid_disposition() -> None:
    tree = build_default_span_tree(  # type: ignore[arg-type]
        **_default_attrs(recommended_disposition="ALLOW"),
    )
    with pytest.raises(SpanContractError, match="not a valid C0 disposition"):
        validate_span_tree(tree)


def test_validate_rejects_forbidden_runtime_token_in_attribute() -> None:
    attrs = _default_attrs()
    # Inject a runtime-disposition token into evidence_status (should be PASS/...).
    attrs["evidence_status"] = "ALLOW"
    tree = build_default_span_tree(**attrs)  # type: ignore[arg-type]
    with pytest.raises(SpanContractError, match="forbidden runtime-disposition token"):
        validate_span_tree(tree)


def test_validate_rejects_forbidden_token_in_child_event() -> None:
    bad_event = C0SpanEvent(name="gate.fail", reason_code="COMMIT_REQUEST")
    children = list(build_default_span_tree(**_default_attrs()).children)  # type: ignore[arg-type]
    # Replace c0.0.preflight with a version that carries the bad event.
    children[0] = C0ChildSpan(
        name="c0.0.preflight",
        invoked=True,
        events=(bad_event,),
    )
    tree = C0SpanTree(parent_attributes=_default_attrs(), children=tuple(children))
    with pytest.raises(SpanContractError, match="forbidden runtime-disposition token"):
        validate_span_tree(tree)


# ---------------------------------------------------------------------------
# Emission + replay determinism.
# ---------------------------------------------------------------------------


def test_emit_records_parent_and_every_child() -> None:
    tracer = InMemoryTracer()
    tree = build_default_span_tree(**_default_attrs())  # type: ignore[arg-type]
    emit_c0_stage_span(tree, tracer)
    assert tracer.parent_name == "c0.stage"
    assert tracer.closed is True
    recorded_names = [c.name for c in tracer.child_records]
    assert recorded_names == list(C0_CHILD_SPAN_NAMES)


def test_emit_marks_unused_lanes_invoked_false() -> None:
    tracer = InMemoryTracer()
    tree = build_default_span_tree(  # type: ignore[arg-type]
        **_default_attrs(),
        extra_lanes_invoked=("dense",),  # only dense
    )
    emit_c0_stage_span(tree, tracer)
    by_name = {c.name: c for c in tracer.child_records}
    assert by_name["c0.2.lane.dense"].invoked is True
    assert by_name["c0.2.lane.sparse"].invoked is False
    assert by_name["c0.2.lane.metadata"].invoked is False
    assert by_name["c0.2.lane.code"].invoked is False


def test_emit_marks_refinement_invoked_false_when_not_run() -> None:
    tracer = InMemoryTracer()
    tree = build_default_span_tree(**_default_attrs())  # type: ignore[arg-type]
    emit_c0_stage_span(tree, tracer)
    by_name = {c.name: c for c in tracer.child_records}
    assert by_name["c0.6.refinement"].invoked is False


def test_emit_marks_refinement_invoked_true_when_run() -> None:
    tracer = InMemoryTracer()
    tree = build_default_span_tree(  # type: ignore[arg-type]
        **_default_attrs(refine_attempts_used=1),
        refinement_invoked=True,
    )
    emit_c0_stage_span(tree, tracer)
    by_name = {c.name: c for c in tracer.child_records}
    assert by_name["c0.6.refinement"].invoked is True


def test_aggregate_hash_replay_stable() -> None:
    tree1 = build_default_span_tree(**_default_attrs())  # type: ignore[arg-type]
    tree2 = build_default_span_tree(**_default_attrs())  # type: ignore[arg-type]
    assert aggregate_span_tree_hash(tree1) == aggregate_span_tree_hash(tree2)


def test_aggregate_hash_changes_when_disposition_changes() -> None:
    a = build_default_span_tree(**_default_attrs(recommended_disposition="proceed"))  # type: ignore[arg-type]
    b = build_default_span_tree(  # type: ignore[arg-type]
        **_default_attrs(recommended_disposition="abstain"),
    )
    assert aggregate_span_tree_hash(a) != aggregate_span_tree_hash(b)


def test_emission_to_two_tracers_records_identical_data() -> None:
    tree = build_default_span_tree(**_default_attrs())  # type: ignore[arg-type]
    t1, t2 = InMemoryTracer(), InMemoryTracer()
    emit_c0_stage_span(tree, t1)
    emit_c0_stage_span(tree, t2)
    assert t1.parent_attributes == t2.parent_attributes
    assert [c.name for c in t1.child_records] == [c.name for c in t2.child_records]
