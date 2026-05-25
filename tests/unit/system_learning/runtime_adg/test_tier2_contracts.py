"""Tests for ``span_contracts.validate_tier2_*`` and Tier 2 emit helpers.

Covers:
  - Tier 2 has exactly 14 stages.
  - Validating an empty snapshot returns 0% coverage.
  - Each emit helper produces a span that satisfies its target Tier 2 stage.
  - Tier 2 span name set matches the SSOT in ``semconv.runtime``.
  - Tier 1 reports continue to work unchanged (additive guarantee).
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from agentic_core.L6_system_learning.runtime_adg import runtime_span_emitter_tier2 as T2
from agentic_core.L6_system_learning.runtime_span_emitter import (
    emit_exit_disposition,
    emit_trace_root,
    seal_step,
)
from agentic_core.L6_system_learning.snapshot import RuntimeADGNode, RuntimeADGSnapshot
from agentic_core.L6_system_learning.span_contracts import (
    SIGNAL_THRESHOLD,
    Tier2Coverage,
    tier2_stage_count,
    tier2_stage_names,
    validate_tier1_coverage,
    validate_tier2_coverage,
)


class _FakeAdapter:
    """Minimal adapter shape consumed by `_append_span`."""

    def __init__(self) -> None:
        self._completed_spans: list[dict[str, Any]] = []


def _build_snapshot(spans: list[dict[str, Any]]) -> RuntimeADGSnapshot:
    """Materialize an OTel-shaped span list into the in-memory ADG snapshot
    used by validators. Avoids the real materializer to keep the test
    self-contained.
    """
    nodes = []
    for s in spans:
        nodes.append(
            RuntimeADGNode(
                node_id=s.get("span_id", "n"),
                name=s.get("name", ""),
                kind=s.get("kind", ""),
                layer=s.get("layer", ""),
                component=s.get("component", "test"),
                started_at_utc=int(s.get("ts_utc", 0)),
                duration_ms=float(s.get("duration_ms", 0.0)),
                status=s.get("status", "ok"),
                attributes_json=json.dumps(s.get("attributes", {})),
            )
        )
    trace_id = spans[0].get("trace_id", "t-test") if spans else "t-test"
    return RuntimeADGSnapshot(
        snapshot_id="snap-test",
        trace_id=trace_id,
        mission="test",
        started_at_utc=0,
        ended_at_utc=0,
        nodes=tuple(nodes),
        edges=(),
        snapshot_hash="hash-test",
    )


# ---------------------------------------------------------------------------
# Tier 2 contract registry
# ---------------------------------------------------------------------------


def test_tier2_has_14_stages():
    assert tier2_stage_count() == 14
    assert len(tier2_stage_names()) == 14


def test_tier2_stage_names_are_ordered():
    names = tier2_stage_names()
    for i, n in enumerate(names, start=1):
        # First two chars after 'stage_' encode the spec stage number.
        prefix = n[len("stage_") : len("stage_") + 2]
        assert prefix == f"{i:02d}", f"expected stage {i:02d}, got {prefix!r} ({n})"


def test_signal_threshold_is_two():
    assert SIGNAL_THRESHOLD == 2


def test_empty_snapshot_zero_coverage():
    snap = RuntimeADGSnapshot(
        snapshot_id="empty",
        trace_id="t0",
        mission="m",
        started_at_utc=0,
        ended_at_utc=0,
        nodes=(),
        edges=(),
        snapshot_hash="h0",
    )
    cov = validate_tier2_coverage(snap)
    assert isinstance(cov, Tier2Coverage)
    assert cov.coverage_pct == 0.0
    assert len(cov.missing_stages) == 14


# ---------------------------------------------------------------------------
# Emit helpers populate Tier 2 stages
# ---------------------------------------------------------------------------


@pytest.fixture
def adapter() -> _FakeAdapter:
    return _FakeAdapter()


def test_emit_intake_satisfies_stage_02(adapter: _FakeAdapter) -> None:
    T2.emit_intake(
        adapter,
        trace_id="t-1",
        request_id="req-1",
        normalized_payload_hash="abc123",
    )
    snap = _build_snapshot(adapter._completed_spans)
    cov = validate_tier2_coverage(snap)
    assert cov.stage_with_attrs["stage_02_intake"], cov.to_dict()


def test_emit_l1_reasoning_satisfies_stage_03(adapter: _FakeAdapter) -> None:
    T2.emit_l1_reasoning(
        adapter,
        trace_id="t-1",
        intent_frame_hash="if-1",
        plan_contract_hash="pc-1",
        proposed_route="R3",
        task_class="research",
    )
    snap = _build_snapshot(adapter._completed_spans)
    cov = validate_tier2_coverage(snap)
    assert cov.stage_with_attrs["stage_03_L1_reasoning"], cov.to_dict()


def test_emit_l0_route_select_satisfies_stage_04(adapter: _FakeAdapter) -> None:
    T2.emit_l0_route_select(
        adapter,
        trace_id="t-1",
        selected_route="R3",
        reason_codes=["evidence_required"],
        route_contract_hash="rc-1",
    )
    snap = _build_snapshot(adapter._completed_spans)
    cov = validate_tier2_coverage(snap)
    assert cov.stage_with_attrs["stage_04_L0_routing"], cov.to_dict()


def test_emit_direct_path_satisfies_stage_05(adapter: _FakeAdapter) -> None:
    T2.emit_direct_path(
        adapter,
        trace_id="t-1",
        direct_step_id="ds-1",
        selected_route="R1",
        packet_hash="ph-1",
    )
    snap = _build_snapshot(adapter._completed_spans)
    cov = validate_tier2_coverage(snap)
    assert cov.stage_with_attrs["stage_05_direct_path"], cov.to_dict()


def test_emit_l3_step_satisfies_stage_06(adapter: _FakeAdapter) -> None:
    T2.emit_l3_step(
        adapter,
        trace_id="t-1",
        workflow_id="wf-1",
        dag_hash="dag-1",
        current_step_id="s1",
        ready_node_ids=["s2"],
        workflow_state_hash="wsh-1",
    )
    snap = _build_snapshot(adapter._completed_spans)
    cov = validate_tier2_coverage(snap)
    assert cov.stage_with_attrs["stage_06_L3_orchestration"], cov.to_dict()


def test_emit_c0_retrieval_satisfies_stage_07(adapter: _FakeAdapter) -> None:
    T2.emit_c0_retrieval(
        adapter,
        trace_id="t-1",
        retrieval_mode="hybrid",
        evidence_ids=["ev-1", "ev-2"],
        vector_store_id="vs-1",
        index_version="idx-v1",
    )
    snap = _build_snapshot(adapter._completed_spans)
    cov = validate_tier2_coverage(snap)
    assert cov.stage_with_attrs["stage_07_C0_retrieval"], cov.to_dict()


def test_emit_c0_retrieval_coerces_invalid_mode(adapter: _FakeAdapter) -> None:
    """Invalid retrieval_mode should be coerced to 'hybrid' fail-open."""
    T2.emit_c0_retrieval(
        adapter,
        trace_id="t-1",
        retrieval_mode="telepathy",  # not in {dense, sparse, hybrid, graph}
        vector_store_id="vs-1",
        index_version="idx-v1",
    )
    # `_append_span` always writes the dict at key 'attributes' (no JSON
    # roundtrip until the snapshot materializer); read from there directly.
    assert len(adapter._completed_spans) == 1
    attrs = adapter._completed_spans[0]["attributes"]
    assert attrs["retrieval_mode"] == "hybrid"


def test_emit_prompt_assembly_satisfies_stage_08(adapter: _FakeAdapter) -> None:
    T2.emit_prompt_assembly(
        adapter,
        trace_id="t-1",
        prompt_envelope_hash="pe-1",
        prompt_hash="ph-1",
        system_template_hash="sth-1",
    )
    snap = _build_snapshot(adapter._completed_spans)
    cov = validate_tier2_coverage(snap)
    assert cov.stage_with_attrs["stage_08_prompt_assembly"], cov.to_dict()


def test_emit_response_satisfies_stage_11(adapter: _FakeAdapter) -> None:
    rid = T2.emit_response(
        adapter,
        trace_id="t-1",
        final_output_hash="foh-1",
    )
    assert rid.startswith("resp-")
    # Two spans should be emitted (Response.emit + Runtime.close_no_write).
    assert len(adapter._completed_spans) == 2
    snap = _build_snapshot(adapter._completed_spans)
    cov = validate_tier2_coverage(snap)
    assert cov.stage_with_attrs["stage_11_response"], cov.to_dict()


def test_emit_uwg_commit_satisfies_stage_12(adapter: _FakeAdapter) -> None:
    cid = T2.emit_uwg_commit(
        adapter,
        trace_id="t-1",
        commit_request_id="cr-1",
        mutation_type="upsert",
        proposed_diff_hash="pdh-1",
        before_hash="bh-1",
        after_hash="ah-1",
        ledger_hash="lh-1",
    )
    assert cid.startswith("commit-")
    snap = _build_snapshot(adapter._completed_spans)
    cov = validate_tier2_coverage(snap)
    assert cov.stage_with_attrs["stage_12_uwg_l4_commit"], cov.to_dict()


def test_emit_l6_eval_satisfies_stage_13(adapter: _FakeAdapter) -> None:
    bid = T2.emit_l6_eval(
        adapter,
        trace_id="t-1",
        replay_digest="rd-1",
        task_completion_score=0.9,
        groundedness_score=0.85,
        trajectory_score=0.8,
    )
    assert bid.startswith("eval-")
    snap = _build_snapshot(adapter._completed_spans)
    cov = validate_tier2_coverage(snap)
    assert cov.stage_with_attrs["stage_13_L6_eval"], cov.to_dict()


def test_emit_meta_learning_satisfies_stage_14(adapter: _FakeAdapter) -> None:
    pcid = T2.emit_meta_learning(
        adapter,
        trace_id="t-1",
        incident_cluster_id="ic-1",
        pattern_id="p-1",
        severity="medium",
    )
    assert pcid.startswith("prom-")
    snap = _build_snapshot(adapter._completed_spans)
    cov = validate_tier2_coverage(snap)
    assert cov.stage_with_attrs["stage_14_meta_learning"], cov.to_dict()


# ---------------------------------------------------------------------------
# End-to-end: every emit helper used in one snapshot fills 13 of 14 stages.
# Stage 07 (C0 retrieval) is fed by rag.py producers, not Tier 2 helpers.
# ---------------------------------------------------------------------------


def test_full_emit_coverage_includes_c0_excludes_l2(adapter: _FakeAdapter) -> None:
    # Tier 1 emitters
    tid = emit_trace_root(adapter, mission="test", trace_id="t-full")
    assert tid == "t-full"
    with seal_step(adapter, step_id="s1", trace_id=tid) as bag:
        bag["output"] = {"final": True}
        bag["evidence_ids"] = ("ev-1",)
    emit_exit_disposition(adapter, trace_id=tid, disposition="allow", policy_hash="ph")
    # Tier 2 emitters
    T2.emit_intake(adapter, trace_id=tid, request_id="r1", normalized_payload_hash="x")
    T2.emit_l1_reasoning(
        adapter,
        trace_id=tid,
        intent_frame_hash="if",
        plan_contract_hash="pc",
        proposed_route="R3",
    )
    T2.emit_l0_route_select(
        adapter,
        trace_id=tid,
        selected_route="R3",
        reason_codes=["x"],
        route_contract_hash="rc",
    )
    T2.emit_direct_path(
        adapter, trace_id=tid, direct_step_id="ds", selected_route="R1", packet_hash="ph"
    )
    T2.emit_l3_step(
        adapter,
        trace_id=tid,
        workflow_id="wf",
        dag_hash="dh",
        current_step_id="s1",
        ready_node_ids=["s2"],
        workflow_state_hash="wsh",
    )
    T2.emit_prompt_assembly(
        adapter,
        trace_id=tid,
        prompt_envelope_hash="pe",
        prompt_hash="phh",
        system_template_hash="sth",
    )
    T2.emit_c0_retrieval(
        adapter,
        trace_id=tid,
        retrieval_mode="hybrid",
        vector_store_id="vs",
        index_version="idx",
    )
    T2.emit_response(adapter, trace_id=tid, final_output_hash="foh")
    T2.emit_uwg_commit(
        adapter,
        trace_id=tid,
        commit_request_id="cr",
        mutation_type="m",
        proposed_diff_hash="pdh",
        before_hash="bh",
        after_hash="ah",
        ledger_hash="lh",
    )
    T2.emit_l6_eval(
        adapter,
        trace_id=tid,
        replay_digest="rd",
        task_completion_score=0.9,
        groundedness_score=0.8,
        trajectory_score=0.7,
    )
    T2.emit_meta_learning(adapter, trace_id=tid, incident_cluster_id="ic", pattern_id="p")

    snap = _build_snapshot(adapter._completed_spans)
    cov = validate_tier2_coverage(snap)
    # All 14 stages should be satisfied: Tier 2 helpers cover 13 stages
    # directly, and Tier 1 ``seal_step`` covers Stage 09 (L2 execution).
    satisfied = {k for k, v in cov.stage_with_attrs.items() if v}
    assert len(satisfied) == 14, cov.to_dict()
    assert cov.coverage_pct == 1.0, cov.to_dict()

    # Tier 1 must also remain satisfied.
    t1 = validate_tier1_coverage(snap)
    assert t1.coverage_pct == 1.0, t1.to_dict()


# ---------------------------------------------------------------------------
# SSOT cross-check
# ---------------------------------------------------------------------------


def test_tier2_emitter_constants_match_semconv():
    """Each SPAN_* in runtime_span_emitter_tier2 must match semconv.runtime."""
    from agentic_core.L6_observability.semconv import runtime as R

    # Every span constant in TIER2 emitter module must be in ALL_SPAN_NAMES.
    missing = T2.ALL_TIER2_SPAN_NAMES - R.ALL_SPAN_NAMES
    assert not missing, f"Tier 2 emitter has spans not in semconv SSOT: {missing}"


def test_every_tier2_stage_has_helper_or_tier1_producer():
    """Every Tier 2 stage MUST have either a Tier 2 emit helper or a Tier 1
    producer. This is the closure guarantee: no stage is left without a
    callable emitter path.

    Stages 01, 09, 10 are produced by Tier 1
    (``emit_trace_root`` / ``seal_step`` / ``emit_exit_disposition``).
    All other stages MUST appear in ``TIER2_EMITTERS``.
    """
    tier1_covered = {"stage_01_trace_root", "stage_09_L2_execution", "stage_10_exit_eval"}
    tier2_covered = set(T2.TIER2_EMITTERS.keys())
    all_stages = set(tier2_stage_names())
    uncovered = all_stages - tier1_covered - tier2_covered
    assert not uncovered, (
        f"Stages without a producer or helper: {uncovered}. "
        "Add a Tier 2 emit helper or document a Tier 1 path."
    )


def test_emit_helpers_fail_open_on_bad_adapter() -> None:
    """Passing an adapter without `_completed_spans` must NOT raise."""

    class BadAdapter:
        pass

    bad = BadAdapter()
    # Each helper must silently no-op (fail-open for observability).
    T2.emit_intake(bad, trace_id="t", request_id="r")
    T2.emit_l1_reasoning(bad, trace_id="t", intent_frame_hash="x", plan_contract_hash="y", proposed_route="R")
    T2.emit_l0_route_select(bad, trace_id="t", selected_route="R")
    T2.emit_direct_path(bad, trace_id="t", direct_step_id="d", selected_route="R", packet_hash="p")
    T2.emit_l3_step(bad, trace_id="t", workflow_id="w", dag_hash="d", current_step_id="s")
    T2.emit_c0_retrieval(bad, trace_id="t", retrieval_mode="hybrid")
    T2.emit_prompt_assembly(bad, trace_id="t", prompt_envelope_hash="p", prompt_hash="h", system_template_hash="s")
    T2.emit_response(bad, trace_id="t", final_output_hash="f")
    T2.emit_uwg_commit(
        bad,
        trace_id="t",
        commit_request_id="c",
        mutation_type="m",
        proposed_diff_hash="p",
        before_hash="b",
        after_hash="a",
        ledger_hash="l",
    )
    T2.emit_l6_eval(bad, trace_id="t")
    T2.emit_meta_learning(bad, trace_id="t")
