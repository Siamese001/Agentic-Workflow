"""Unit tests for Phase C.2 — pure trace-row normalizer.

All tests use synthetic ``ContractSpanBinding`` fixtures and ``PhaseC1Row``
objects built without any live SQLite / RuntimeADGQuery dependency.

Test plan reference: task spec §8 (14 required tests)
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from agentic_core.L6_system_learning.app_route_contracts import (
    CertificationLevel,
    ContractSpanBinding,
    PhaseAStatus,
    RequiredAttribute,
    RouteShape,
    build_r3_grounded_read_contract,
)
from tools.runtime_cert.runtime_adg_query_adapter import (
    NOT_CERTIFIED,
    PhaseC1Row,
)
from tools.runtime_cert.trace_row_normalizer import (
    ATTRIBUTE_HARDENING_REQUIRED,
    EXISTS_MATCHES_MATRIX,
    EXISTS_NAME_MISMATCH,
    EXISTS_NEEDS_ATTRIBUTE_HARDENING,
    FORBIDDEN_SPAN_VIOLATION,
    LEDGER_EVENT_ONLY,
    NOT_FOUND,
    STUB_ONLY,
    TELEMETRY_MARKER_ONLY,
    UNKNOWN_NEEDS_RUNTIME_RUN,
    NormalizedTraceRow,
    normalize_trace_row,
    normalize_trace_rows,
)

# ---------------------------------------------------------------------------
# Shared fixture factories
# ---------------------------------------------------------------------------


def _req_attr(name: str) -> RequiredAttribute:
    return RequiredAttribute(
        name=name,
        required=True,
        description=f"Test attribute {name}",
        failure_if_missing=f"attribute_missing:{name}",
    )


def _binding(
    contract_name: str,
    alias: str,
    *,
    categories: tuple[str, ...] = (),
    name_patterns: tuple[str, ...] = (),
    emitter_files: tuple[str, ...] = (),
    phase_a: PhaseAStatus = PhaseAStatus.EXISTS_MATCHES_MATRIX,
    required_attrs: tuple[RequiredAttribute, ...] = (),
    live_trace_required: bool = False,
) -> ContractSpanBinding:
    if phase_a in (PhaseAStatus.UNKNOWN_NEEDS_RUNTIME_RUN, PhaseAStatus.NOT_FOUND):
        live_trace_required = True
    return ContractSpanBinding(
        contract_name=contract_name,
        normalized_cert_alias=alias,
        accepted_emitter_categories=categories,
        accepted_span_name_patterns=name_patterns,
        accepted_emitter_files=emitter_files,
        phase_a_status=phase_a,
        required_attributes=required_attrs,
        live_trace_required=live_trace_required,
        failure_conditions=("span missing",),
    )


def _row(
    span_name: str = "test.span",
    span_id: str = "s1",
    app_name: str = "apps_research",
    route_shape: str = "R3_grounded_read",
    attrs: dict[str, Any] | None = None,
    source_path: str | None = None,
    contract_name: str | None = None,
    normalized_cert_alias: str | None = None,
) -> PhaseC1Row:
    return PhaseC1Row(
        app_name=app_name,
        route_shape=route_shape,
        trace_id="trace-test",
        span_id=span_id,
        parent_span_id=None,
        span_name=span_name,
        timestamp=1_000_000,
        contract_name=contract_name,
        normalized_cert_alias=normalized_cert_alias,
        manifest_hash="",
        static_runtime_mode="",
        runtime_certification_status=NOT_CERTIFIED,
        artifact_id=None,
        contract_id=None,
        source_path=source_path,
        attributes=attrs or {},
        evidence_source="runtime_adg.snapshot.abc123",
    )


# ---------------------------------------------------------------------------
# Test 1 — Tier-1 category match (P1)
# ---------------------------------------------------------------------------


def test_p1_tier1_category_maps_route_contract():
    """T1: Tier-1 L0.route.select category maps to RouteContract binding."""
    b = _binding(
        "RouteContract",
        "app.apps_research.l0.route_contract",
        categories=("L0.route.select",),
        name_patterns=("heal_router", "route.select"),
        phase_a=PhaseAStatus.EXISTS_MATCHES_MATRIX,
    )
    # Provide signals: name_pattern + layer attr + routing attr = 3 signals
    row = _row(
        span_name="heal_router.v1.route",
        attrs={"layer": "L0", "selected_route": "R3_grounded_read"},
    )
    result = normalize_trace_row(row, [b])
    assert result.contract_name == "RouteContract"
    assert result.normalized_cert_alias == "app.apps_research.l0.route_contract"
    assert "P1" in result.match_basis
    assert result.runtime_certification_status == NOT_CERTIFIED


def test_p1_tier1_sealed_artifact():
    """T1b: Tier-1 L2.step.seal maps to SealedArtifact binding."""
    b = _binding(
        "SealedArtifact",
        "app.apps_research.l2.sealed_artifact",
        name_patterns=("l2.step.seal", "step.seal"),
        phase_a=PhaseAStatus.EXISTS_MATCHES_MATRIX,
    )
    row = _row(
        span_name="l2.step.seal",
        attrs={"layer": "L2", "output_hash": "abc"},
    )
    result = normalize_trace_row(row, [b])
    assert result.contract_name == "SealedArtifact"
    assert "P1" in result.match_basis


# ---------------------------------------------------------------------------
# Test 2 — GenAI semconv attribute match (P2)
# ---------------------------------------------------------------------------


def test_p2_genai_semconv_maps_compiled_prompt():
    """T2: gen_ai.operation.name present maps to CompiledPromptArtifact."""
    b = _binding(
        "CompiledPromptArtifact",
        "app.apps_research.pa.compiled_prompt_artifact",
        categories=("GenAI.semconv", "L2.model.invoke"),
        name_patterns=("invoke_agent",),
        phase_a=PhaseAStatus.EXISTS_NEEDS_ATTRIBUTE_HARDENING,
    )
    row = _row(
        span_name="some.unknown.span",
        attrs={"gen_ai.operation.name": "invoke_agent", "gen_ai.system": "openai"},
    )
    result = normalize_trace_row(row, [b])
    assert result.contract_name == "CompiledPromptArtifact"
    assert "P2" in result.match_basis
    assert "gen_ai" in result.match_basis


def test_p2_genai_system_attr_only():
    """T2b: gen_ai.system alone triggers P2 match."""
    b = _binding(
        "CompiledPromptArtifact",
        "app.apps_research.pa.compiled_prompt_artifact",
        categories=("GenAI.semconv",),
        phase_a=PhaseAStatus.EXISTS_NEEDS_ATTRIBUTE_HARDENING,
    )
    row = _row(
        span_name="model.call",
        attrs={"gen_ai.system": "anthropic"},
    )
    result = normalize_trace_row(row, [b])
    assert result.contract_name == "CompiledPromptArtifact"
    assert "P2" in result.match_basis


# ---------------------------------------------------------------------------
# Test 3 — span name pattern match (P3)
# ---------------------------------------------------------------------------


def test_p3_name_pattern_maps_exit_review():
    """T3: accepted_span_name_patterns match → ExitReviewPacket."""
    b = _binding(
        "ExitReviewPacket",
        "app.apps_research.exit.review_packet",
        name_patterns=("exit.disposition", "exit.*", "disposition.*"),
        phase_a=PhaseAStatus.EXISTS_MATCHES_MATRIX,
    )
    row = _row(span_name="exit.disposition.v6")
    result = normalize_trace_row(row, [b])
    assert result.contract_name == "ExitReviewPacket"
    assert "P3" in result.match_basis


def test_p3_name_pattern_partial_match():
    """T3b: partial substring pattern match works."""
    b = _binding(
        "L1PlanContract",
        "app.apps_research.l1.plan_contract",
        name_patterns=("l1.plan", "planning."),
        phase_a=PhaseAStatus.EXISTS_NEEDS_ATTRIBUTE_HARDENING,
    )
    row = _row(span_name="l1.plan.emit")
    result = normalize_trace_row(row, [b])
    assert result.contract_name == "L1PlanContract"
    assert "P3" in result.match_basis


# ---------------------------------------------------------------------------
# Test 4 — emitter file match (P4)
# ---------------------------------------------------------------------------


def test_p4_emitter_file_maps_validated_request():
    """T4: accepted_emitter_files match via source_path → ValidatedRequest."""
    b = _binding(
        "ValidatedRequest",
        "app.apps_research.intake.validated_request",
        emitter_files=("agentic_core/L5_safety/enforcement/ingress_telemetry_otel.py",),
        phase_a=PhaseAStatus.EXISTS_NAME_MISMATCH,
    )
    row = _row(
        span_name="some.ingress.op",
        source_path="agentic_core/L5_safety/enforcement/ingress_telemetry_otel.py",
    )
    result = normalize_trace_row(row, [b])
    assert result.contract_name == "ValidatedRequest"
    assert "P4" in result.match_basis


def test_p4_emitter_file_from_attrs():
    """T4b: code.filepath in attributes is used when source_path is None."""
    b = _binding(
        "ValidatedRequest",
        "app.apps_research.intake.validated_request",
        emitter_files=("agentic_core/L5_safety/enforcement/ingress_telemetry_otel.py",),
        phase_a=PhaseAStatus.EXISTS_NAME_MISMATCH,
    )
    row = _row(
        span_name="some.span",
        attrs={"code.filepath": "agentic_core/L5_safety/enforcement/ingress_telemetry_otel.py"},
    )
    result = normalize_trace_row(row, [b])
    assert result.contract_name == "ValidatedRequest"
    assert "P4" in result.match_basis


# ---------------------------------------------------------------------------
# Test 5 — direct attributes.contract_name fallback (P5)
# ---------------------------------------------------------------------------


def test_p5_direct_attr_contract_name():
    """T5: attributes['contract_name'] fallback works when no P1-P4 match."""
    b = _binding(
        "RetrievalPlan",
        "app.apps_research.c0.retrieval_plan",
        phase_a=PhaseAStatus.EXISTS_NEEDS_ATTRIBUTE_HARDENING,
    )
    row = _row(
        span_name="totally.unknown.span.xyz",
        attrs={"contract_name": "RetrievalPlan"},
    )
    result = normalize_trace_row(row, [b])
    assert result.contract_name == "RetrievalPlan"
    assert "P5" in result.match_basis


# ---------------------------------------------------------------------------
# Test 6 — precedence: P1 beats P5 conflict
# ---------------------------------------------------------------------------


def test_precedence_p1_beats_p5():
    """T6: P1 Tier-1 match takes precedence over conflicting P5 direct attr."""
    b_route = _binding(
        "RouteContract",
        "app.apps_research.l0.route_contract",
        name_patterns=("heal_router",),
        phase_a=PhaseAStatus.EXISTS_MATCHES_MATRIX,
    )
    b_retrieval = _binding(
        "RetrievalPlan",
        "app.apps_research.c0.retrieval_plan",
        phase_a=PhaseAStatus.EXISTS_NEEDS_ATTRIBUTE_HARDENING,
    )
    # P1 signals: name matches RouteContract; P5 attr says RetrievalPlan
    row = _row(
        span_name="heal_router.v1.route",
        attrs={
            "layer": "L0",
            "selected_route": "R3",
            "contract_name": "RetrievalPlan",  # would be P5
        },
    )
    result = normalize_trace_row(row, [b_route, b_retrieval])
    # P1 must win
    assert result.contract_name == "RouteContract"
    assert "P1" in result.match_basis


# ---------------------------------------------------------------------------
# Test 7 — missing required attributes → ATTRIBUTE_HARDENING_REQUIRED
# ---------------------------------------------------------------------------


def test_missing_required_attrs_produces_hardening_required():
    """T7: binding matches but required attributes absent → ATTRIBUTE_HARDENING_REQUIRED."""
    b = _binding(
        "SealedArtifact",
        "app.apps_research.l2.sealed_artifact",
        name_patterns=("l2.step.seal",),
        phase_a=PhaseAStatus.EXISTS_NEEDS_ATTRIBUTE_HARDENING,
        required_attrs=(
            _req_attr("app_name"),
            _req_attr("manifest_hash"),
            _req_attr("contract_id"),
        ),
    )
    # Row matches P3 name pattern but lacks manifest_hash and contract_id
    row = _row(
        span_name="l2.step.seal",
        app_name="apps_research",
        attrs={"app_name": "apps_research"},  # contract_id and manifest_hash missing
    )
    result = normalize_trace_row(row, [b])
    assert result.phase_c_status == ATTRIBUTE_HARDENING_REQUIRED
    assert result.contract_name == "SealedArtifact"
    assert "manifest_hash" in result.mapping_notes or "contract_id" in result.mapping_notes


# ---------------------------------------------------------------------------
# Test 8 — no match → UNKNOWN_NEEDS_RUNTIME_RUN
# ---------------------------------------------------------------------------


def test_no_match_produces_unknown_needs_runtime_run():
    """T8: no binding matches any priority → UNKNOWN_NEEDS_RUNTIME_RUN."""
    b = _binding(
        "ValidatedRequest",
        "app.apps_research.intake.validated_request",
        categories=("L5.ingress.telemetry",),
        name_patterns=("ingress.*",),
        phase_a=PhaseAStatus.EXISTS_NAME_MISMATCH,
    )
    row = _row(span_name="completely.unrelated.span.noop.xyz123")
    result = normalize_trace_row(row, [b])
    assert result.phase_c_status == UNKNOWN_NEEDS_RUNTIME_RUN
    assert result.contract_name is None
    assert result.normalized_cert_alias is None


# ---------------------------------------------------------------------------
# Test 9 — CommitRequest on R3 app → FORBIDDEN_SPAN_VIOLATION, row preserved
# ---------------------------------------------------------------------------


def test_commit_request_on_r3_app_forbidden():
    """T9: CommitRequest span on R3 app → FORBIDDEN_SPAN_VIOLATION, row preserved."""
    b = _binding(
        "RouteContract",
        "app.apps_research.l0.route_contract",
        name_patterns=("route.select",),
        phase_a=PhaseAStatus.EXISTS_MATCHES_MATRIX,
    )
    row = _row(
        span_name="CommitRequest",
        app_name="apps_research",
        route_shape="R3_grounded_read",
    )
    result = normalize_trace_row(row, [b])
    assert result.phase_c_status == FORBIDDEN_SPAN_VIOLATION
    assert result.span_id == "s1"  # row is preserved
    assert result.span_name == "CommitRequest"
    assert result.runtime_certification_status == NOT_CERTIFIED


def test_commit_request_via_attr_on_r3():
    """T9b: attributes['contract_name']='CommitRequest' on R3 app → FORBIDDEN_SPAN_VIOLATION."""
    b = _binding("RouteContract", "alias", phase_a=PhaseAStatus.EXISTS_MATCHES_MATRIX)
    row = _row(
        span_name="some.normal.span",
        route_shape="R3_grounded_read",
        attrs={"contract_name": "CommitRequest"},
    )
    result = normalize_trace_row(row, [b])
    assert result.phase_c_status == FORBIDDEN_SPAN_VIOLATION


def test_commit_request_on_non_r3_not_forbidden():
    """T9c: CommitRequest on a non-R3 app is NOT flagged as FORBIDDEN_SPAN_VIOLATION."""
    b = _binding(
        "CommitRequest",
        "app.apps_durable.commit_request",
        name_patterns=("CommitRequest",),
        phase_a=PhaseAStatus.EXISTS_MATCHES_MATRIX,
    )
    row = _row(
        span_name="CommitRequest",
        app_name="apps_durable",
        route_shape="R3R4_grounded_write",
    )
    result = normalize_trace_row(row, [b])
    # R3R4 is in _R3_ROUTE_SHAPES so it IS forbidden — verify explicitly
    assert result.phase_c_status == FORBIDDEN_SPAN_VIOLATION


# ---------------------------------------------------------------------------
# Test 10 — runtime_certification_status invariant
# ---------------------------------------------------------------------------


def test_runtime_certification_status_always_not_certified():
    """T10: NormalizedTraceRow rejects any non-NOT_CERTIFIED value."""
    with pytest.raises(ValueError, match="NOT_CERTIFIED"):
        NormalizedTraceRow(
            app_name="apps_research",
            route_shape="R3_grounded_read",
            trace_id="t1",
            span_id="s1",
            parent_span_id=None,
            span_name="test",
            timestamp=0,
            contract_name=None,
            normalized_cert_alias=None,
            phase_c_status=UNKNOWN_NEEDS_RUNTIME_RUN,
            match_basis="",
            mapping_notes="",
            binding_contract_name=None,
            runtime_certification_status="RUNTIME_CERTIFIED",
        )


def test_normalized_row_has_not_certified_by_default():
    """T10b: normalize_trace_row output always carries NOT_CERTIFIED status."""
    b = _binding("RouteContract", "alias", name_patterns=("route",),
                 phase_a=PhaseAStatus.EXISTS_MATCHES_MATRIX)
    row = _row(span_name="route.select")
    result = normalize_trace_row(row, [b])
    assert result.runtime_certification_status == NOT_CERTIFIED


# ---------------------------------------------------------------------------
# Test 11 — attributes are preserved intact
# ---------------------------------------------------------------------------


def test_attributes_preserved_intact():
    """T11: all attributes from the C.1 row are preserved unchanged in NormalizedTraceRow."""
    original_attrs = {
        "app_name": "apps_research",
        "run_id": "run-42",
        "contract_name": "SealedArtifact",
        "custom_field": "preserved",
    }
    b = _binding(
        "SealedArtifact",
        "app.apps_research.l2.sealed_artifact",
        phase_a=PhaseAStatus.EXISTS_MATCHES_MATRIX,
    )
    row = _row(span_name="test.span", attrs=original_attrs)
    result = normalize_trace_row(row, [b])
    assert result.attributes == original_attrs
    assert result.attributes["custom_field"] == "preserved"


# ---------------------------------------------------------------------------
# Test 12 — to_dict serialization
# ---------------------------------------------------------------------------


def test_to_dict_serialisable():
    """T12: NormalizedTraceRow.to_dict() passes json.dumps without raising."""
    b = _binding(
        "ExitReviewPacket",
        "app.apps_research.exit.review_packet",
        name_patterns=("exit.disposition",),
        phase_a=PhaseAStatus.EXISTS_MATCHES_MATRIX,
    )
    row = _row(span_name="exit.disposition.v6", attrs={"foo": 42})
    result = normalize_trace_row(row, [b])
    d = result.to_dict()
    serialised = json.dumps(d)
    assert isinstance(serialised, str)
    assert "NOT_CERTIFIED" in serialised
    assert "ExitReviewPacket" in serialised


def test_to_dict_contains_phase_c_fields():
    """T12b: to_dict contains all Phase C.2-specific fields."""
    b = _binding("RouteContract", "alias", name_patterns=("route",),
                 phase_a=PhaseAStatus.EXISTS_MATCHES_MATRIX)
    row = _row(span_name="route.select")
    result = normalize_trace_row(row, [b])
    d = result.to_dict()
    for key in ("phase_c_status", "match_basis", "mapping_notes", "binding_contract_name"):
        assert key in d, f"Key {key!r} missing from to_dict output"


# ---------------------------------------------------------------------------
# Test 13 — normalize_trace_rows preserves input order
# ---------------------------------------------------------------------------


def test_normalize_trace_rows_preserves_order():
    """T13: normalize_trace_rows returns rows in same order as input."""
    bindings = [
        _binding("RouteContract", "alias_a", name_patterns=("route.alpha",),
                 phase_a=PhaseAStatus.EXISTS_MATCHES_MATRIX),
        _binding("SealedArtifact", "alias_b", name_patterns=("step.beta",),
                 phase_a=PhaseAStatus.EXISTS_MATCHES_MATRIX),
        _binding("ExitReviewPacket", "alias_c", name_patterns=("exit.gamma",),
                 phase_a=PhaseAStatus.EXISTS_MATCHES_MATRIX),
    ]
    rows = [
        _row(span_name="route.alpha", span_id="s1"),
        _row(span_name="step.beta", span_id="s2"),
        _row(span_name="exit.gamma", span_id="s3"),
        _row(span_name="unmatched.xyz", span_id="s4"),
    ]
    results = normalize_trace_rows(rows, bindings)
    assert len(results) == 4
    assert results[0].span_id == "s1"
    assert results[1].span_id == "s2"
    assert results[2].span_id == "s3"
    assert results[3].span_id == "s4"
    assert results[0].contract_name == "RouteContract"
    assert results[1].contract_name == "SealedArtifact"
    assert results[2].contract_name == "ExitReviewPacket"
    assert results[3].contract_name is None


# ---------------------------------------------------------------------------
# Test 14 — B.5 negative-control accessors work on normalized rows
# ---------------------------------------------------------------------------


def test_b5_accessors_work_on_normalized_rows():
    """T14: B.5 defensive accessor functions work on NormalizedTraceRow.to_dict()."""
    from tools.runtime_cert.negative_controls import (
        _row_app_name,
        _row_contract_name,
        _row_source_path,
    )

    b = _binding(
        "SealedArtifact",
        "app.apps_research.l2.sealed_artifact",
        name_patterns=("l2.step.seal",),
        phase_a=PhaseAStatus.EXISTS_MATCHES_MATRIX,
    )
    row = _row(
        span_name="l2.step.seal",
        app_name="apps_research",
        attrs={"app_name": "apps_research"},
        source_path="agentic_core/L2_execution/observability/l2_otel_emitter.py",
    )
    result = normalize_trace_row(row, [b])
    d = result.to_dict()

    assert _row_app_name(d) == "apps_research"
    # contract_name is resolved by C.2, so B.5 accessor sees it
    assert _row_contract_name(d) == "SealedArtifact"
    assert _row_source_path(d) is not None


# ---------------------------------------------------------------------------
# Additional: phase_a_status → phase_c_status mapping
# ---------------------------------------------------------------------------


def test_phase_a_exists_matches_matrix_maps_to_phase_c():
    """EXISTS_MATCHES_MATRIX phase_a_status produces EXISTS_MATCHES_MATRIX phase_c_status."""
    b = _binding(
        "ExitReviewPacket",
        "app.apps_research.exit.review_packet",
        name_patterns=("exit.disposition",),
        phase_a=PhaseAStatus.EXISTS_MATCHES_MATRIX,
    )
    row = _row(span_name="exit.disposition")
    result = normalize_trace_row(row, [b])
    assert result.phase_c_status == EXISTS_MATCHES_MATRIX


def test_phase_a_unknown_maps_to_unknown_with_live_trace_note():
    """UNKNOWN_NEEDS_RUNTIME_RUN phase_a forces live_trace_required note."""
    b = _binding(
        "FinalEvidenceContract",
        "app.apps_research.c0.final_evidence_contract",
        name_patterns=("c0.final_evidence",),
        phase_a=PhaseAStatus.UNKNOWN_NEEDS_RUNTIME_RUN,
        live_trace_required=True,
    )
    row = _row(span_name="c0.final_evidence.emit")
    result = normalize_trace_row(row, [b])
    assert result.phase_c_status == UNKNOWN_NEEDS_RUNTIME_RUN
    assert "live_trace_required" in result.mapping_notes


# ---------------------------------------------------------------------------
# Additional: normalize_trace_rows on empty input
# ---------------------------------------------------------------------------


def test_normalize_trace_rows_empty():
    """normalize_trace_rows on empty input returns empty tuple."""
    results = normalize_trace_rows([], [])
    assert results == ()


# ---------------------------------------------------------------------------
# Additional: evidence_source preserved from C.1
# ---------------------------------------------------------------------------


def test_evidence_source_preserved():
    """evidence_source from C.1 row is carried through unchanged."""
    b = _binding("RouteContract", "alias", name_patterns=("route",),
                 phase_a=PhaseAStatus.EXISTS_MATCHES_MATRIX)
    row = _row(span_name="route.select")
    result = normalize_trace_row(row, [b])
    assert result.evidence_source == "runtime_adg.snapshot.abc123"


# ---------------------------------------------------------------------------
# Additional: real R3 bindings via build_r3_grounded_read_contract
# ---------------------------------------------------------------------------


def test_real_r3_bindings_route_contract_p1():
    """Integration: real R3 bindings; heal_router span matches RouteContract at P1."""
    contract = build_r3_grounded_read_contract(
        app_name="apps_research",
        manifest_path="apps_research/spine_manifest.yaml",
        manifest_hash="a" * 64,
    )
    row = _row(
        span_name="heal_router.v1.route",
        attrs={"layer": "L0", "selected_route": "R3_grounded_read"},
    )
    result = normalize_trace_row(row, list(contract.bindings))
    assert result.contract_name == "RouteContract"
    assert "P1" in result.match_basis


def test_real_r3_bindings_exit_review_p3():
    """Integration: real R3 bindings; exit.disposition span matches ExitReviewPacket at P3."""
    contract = build_r3_grounded_read_contract(
        app_name="apps_research",
        manifest_path="apps_research/spine_manifest.yaml",
        manifest_hash="b" * 64,
    )
    row = _row(span_name="exit.disposition.check")
    result = normalize_trace_row(row, list(contract.bindings))
    assert result.contract_name == "ExitReviewPacket"


# ---------------------------------------------------------------------------
# Additional: normalize_trace_rows reuses binding list (not consumed per row)
# ---------------------------------------------------------------------------


def test_normalize_trace_rows_binding_reuse():
    """normalize_trace_rows materialises bindings once; all rows can match."""
    b = _binding(
        "SealedArtifact", "alias",
        name_patterns=("l2.step.seal",),
        phase_a=PhaseAStatus.EXISTS_MATCHES_MATRIX,
    )
    rows = [_row(span_name="l2.step.seal", span_id=f"s{i}") for i in range(5)]
    results = normalize_trace_rows(rows, [b])
    assert all(r.contract_name == "SealedArtifact" for r in results)
