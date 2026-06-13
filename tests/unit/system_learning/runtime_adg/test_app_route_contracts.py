"""Tier 2 per-app-route contract schema tests (Phase B.2).

Pins the invariants defined in
``system_learning/runtime_adg/app_route_contracts.py`` and the design
matrix v2 at ``docs/reference/runtime_certification/contract_span_binding_matrix.md``.

No runtime certification happens here. The tests exercise schema
construction, validation rules, and serialization round-trip only.
"""

from __future__ import annotations

import pytest

from agentic_core.L6_system_learning.app_route_contracts import (
    AppRouteContract,
    BUILD_TIME_COMPILER_CONTRACTS,
    BUILD_TIME_COMPILER_FORBIDDEN_CONTRACTS,
    CertificationLevel,
    ContractSpanBinding,
    PhaseAStatus,
    R3_GROUNDED_READ_CONTRACTS,
    RequiredAttribute,
    RouteShape,
    build_build_time_compiler_contract,
    build_formal_exception_contract,
    build_r3_grounded_read_contract,
)


# ---------------------------------------------------------------------------
# R3_grounded_read factory
# ---------------------------------------------------------------------------


def test_r3_factory_includes_exactly_the_8_canonical_contracts() -> None:
    c = build_r3_grounded_read_contract(
        app_name="apps_research",
        manifest_path="apps_research/spine_manifest.yaml",
        manifest_hash="",  # empty allowed at STATIC_EVIDENCE level
    )
    assert c.route_shape == RouteShape.R3_grounded_read
    assert tuple(c.required_contracts) == R3_GROUNDED_READ_CONTRACTS
    assert len(c.required_contracts) == 8
    # 8 bindings, one per canonical contract, in design-matrix order.
    assert len(c.bindings) == 8
    for expected, binding in zip(R3_GROUNDED_READ_CONTRACTS, c.bindings):
        assert binding.contract_name == expected


def test_r3_factory_forbids_CommitRequest() -> None:
    c = build_r3_grounded_read_contract(
        app_name="apps_research",
        manifest_path="apps_research/spine_manifest.yaml",
        manifest_hash="",
    )
    assert "CommitRequest" in c.forbidden_contracts


def test_r3_factory_requires_CommitRequest_forbidden_explicitly() -> None:
    """Hand-constructing an R3 contract without forbidding CommitRequest must fail."""
    with pytest.raises(ValueError, match="CommitRequest MUST be in forbidden_contracts"):
        AppRouteContract(
            app_name="apps_research",
            route_shape=RouteShape.R3_grounded_read,
            static_runtime_mode="APP_OVERLAY_STATIC_EVIDENCE",
            manifest_path="apps_research/spine_manifest.yaml",
            manifest_hash="",
            certification_level=CertificationLevel.STATIC_EVIDENCE,
            required_contracts=R3_GROUNDED_READ_CONTRACTS,
            bindings=(),  # bindings empty is allowed; the forbidden-set check fires first
            forbidden_contracts=frozenset(),  # offender
        )


def test_r3_factory_rejects_missing_canonical_contract() -> None:
    shortened = tuple(c for c in R3_GROUNDED_READ_CONTRACTS if c != "RouteContract")
    with pytest.raises(ValueError, match="missing canonical R3 entries"):
        AppRouteContract(
            app_name="apps_research",
            route_shape=RouteShape.R3_grounded_read,
            static_runtime_mode="APP_OVERLAY_STATIC_EVIDENCE",
            manifest_path="apps_research/spine_manifest.yaml",
            manifest_hash="",
            certification_level=CertificationLevel.STATIC_EVIDENCE,
            required_contracts=shortened,
            bindings=(),
            forbidden_contracts=frozenset({"CommitRequest"}),
        )


def test_r3_PromptEnvelope_satisfies_CompiledPromptArtifact() -> None:
    """The equivalence group CompiledPromptArtifact <-> PromptEnvelope must
    be honored in the required-contract check (apps_rg uses PromptEnvelope)."""
    with_envelope = tuple(
        "PromptEnvelope" if c == "CompiledPromptArtifact" else c
        for c in R3_GROUNDED_READ_CONTRACTS
    )
    contract = AppRouteContract(
        app_name="apps_rg",
        route_shape=RouteShape.R3_grounded_read,
        static_runtime_mode="APP_OVERLAY_STATIC_EVIDENCE",
        manifest_path="apps_rg/spine_manifest.yaml",
        manifest_hash="",
        certification_level=CertificationLevel.STATIC_EVIDENCE,
        required_contracts=with_envelope,
        bindings=(),
        forbidden_contracts=frozenset({"CommitRequest"}),
    )
    assert "PromptEnvelope" in contract.required_contracts
    assert "CompiledPromptArtifact" not in contract.required_contracts


# ---------------------------------------------------------------------------
# build_time_compiler factory
# ---------------------------------------------------------------------------


def test_build_time_compiler_factory_excludes_R3_chain() -> None:
    c = build_build_time_compiler_contract(
        app_name="apps_qna",
        manifest_path="apps_qna/spine_manifest.yaml",
        manifest_hash="",
    )
    assert c.route_shape == RouteShape.build_time_compiler
    assert tuple(c.required_contracts) == BUILD_TIME_COMPILER_CONTRACTS
    # NO R3-chain contract may appear in required_contracts.
    for forbidden in BUILD_TIME_COMPILER_FORBIDDEN_CONTRACTS:
        assert forbidden not in c.required_contracts


def test_build_time_compiler_rejects_R3_chain_in_required_contracts() -> None:
    with pytest.raises(ValueError, match="must NOT include R3-chain entries"):
        AppRouteContract(
            app_name="apps_qna",
            route_shape=RouteShape.build_time_compiler,
            static_runtime_mode="APP_OVERLAY_STATIC_EVIDENCE",
            manifest_path="apps_qna/spine_manifest.yaml",
            manifest_hash="",
            certification_level=CertificationLevel.STATIC_EVIDENCE,
            required_contracts=(
                "ValidatedRequest",
                "SealedArtifact",  # offender
            ),
            bindings=(),
        )


# ---------------------------------------------------------------------------
# Formal exception factory
# ---------------------------------------------------------------------------


def test_formal_exception_factory_requires_compensating_controls() -> None:
    with pytest.raises(ValueError, match="compensating_controls must be"):
        build_formal_exception_contract(
            app_name="apps_eval",
            route_shape=RouteShape.evaluator_only,
            manifest_path="apps_eval/spine_manifest.yaml",
            manifest_hash="",
            reason_code="evaluator_isolation",
            compensating_controls=(),  # offender
        )


def test_formal_exception_factory_rejects_non_exception_route() -> None:
    with pytest.raises(ValueError, match="route_shape must be one of"):
        build_formal_exception_contract(
            app_name="apps_research",
            route_shape=RouteShape.R3_grounded_read,  # offender
            manifest_path="apps_research/spine_manifest.yaml",
            manifest_hash="",
            reason_code="irrelevant",
            compensating_controls=("CC-X-01",),
        )


def test_formal_exception_factory_succeeds_for_apps_shared() -> None:
    c = build_formal_exception_contract(
        app_name="apps_shared",
        route_shape=RouteShape.core_adjacent_utility,
        manifest_path="apps_shared/spine_manifest.yaml",
        manifest_hash="",
        reason_code="shared_library_surface",
        compensating_controls=(
            "CC-SHARED-01",
            "CC-SHARED-02",
            "CC-SHARED-03",
            "CC-SHARED-04",
            "CC-SHARED-05",
        ),
    )
    assert c.required_contracts == ()
    assert c.bindings == ()
    assert c.formal_exception_reason_code == "shared_library_surface"
    assert len(c.compensating_controls) == 5


def test_formal_exception_level_without_controls_is_rejected() -> None:
    """Even a non-exception route_shape, if upgraded to
    FORMAL_EXCEPTION_VERIFIED, must carry compensating_controls."""
    with pytest.raises(ValueError, match="requires non-empty compensating_controls"):
        AppRouteContract(
            app_name="apps_research",
            route_shape=RouteShape.R3_grounded_read,
            static_runtime_mode="APP_OVERLAY_STATIC_EVIDENCE",
            manifest_path="apps_research/spine_manifest.yaml",
            manifest_hash="sha256:abc",
            certification_level=CertificationLevel.FORMAL_EXCEPTION_VERIFIED,
            required_contracts=R3_GROUNDED_READ_CONTRACTS,
            bindings=(),
            forbidden_contracts=frozenset({"CommitRequest"}),
            compensating_controls=(),  # offender
        )


# ---------------------------------------------------------------------------
# manifest_hash rule
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "level",
    [
        CertificationLevel.TRACE_OBSERVED,
        CertificationLevel.RUNTIME_CERTIFIED,
        CertificationLevel.FORMAL_EXCEPTION_VERIFIED,
    ],
)
def test_manifest_hash_required_for_trace_observed_or_higher(
    level: CertificationLevel,
) -> None:
    with pytest.raises(ValueError, match="manifest_hash must be"):
        AppRouteContract(
            app_name="apps_research",
            route_shape=RouteShape.R3_grounded_read,
            static_runtime_mode="APP_OVERLAY_STATIC_EVIDENCE",
            manifest_path="apps_research/spine_manifest.yaml",
            manifest_hash="",  # offender at this level
            certification_level=level,
            required_contracts=R3_GROUNDED_READ_CONTRACTS,
            bindings=(),
            forbidden_contracts=frozenset({"CommitRequest"}),
            compensating_controls=("CC-X-01",)
            if level == CertificationLevel.FORMAL_EXCEPTION_VERIFIED
            else (),
        )


def test_manifest_hash_empty_allowed_at_static_evidence() -> None:
    """STATIC_EVIDENCE is the post-W14 baseline; empty manifest_hash is
    explicitly allowed there."""
    c = build_r3_grounded_read_contract(
        app_name="apps_research",
        manifest_path="apps_research/spine_manifest.yaml",
        manifest_hash="",  # allowed at STATIC_EVIDENCE
    )
    assert c.certification_level == CertificationLevel.STATIC_EVIDENCE
    assert c.manifest_hash == ""


# ---------------------------------------------------------------------------
# Ambiguous Phase A status rule
# ---------------------------------------------------------------------------


def _std_attrs() -> tuple[RequiredAttribute, ...]:
    return (
        RequiredAttribute(
            name="app_name",
            required=True,
            description="app name",
            failure_if_missing="attribute_missing:app_name",
        ),
    )


@pytest.mark.parametrize(
    "ambiguous",
    [PhaseAStatus.UNKNOWN_NEEDS_RUNTIME_RUN, PhaseAStatus.NOT_FOUND],
)
def test_ambiguous_phase_a_status_forces_live_trace_required(
    ambiguous: PhaseAStatus,
) -> None:
    with pytest.raises(ValueError, match="live_trace_required MUST be True"):
        ContractSpanBinding(
            contract_name="FinalEvidenceContract",
            normalized_cert_alias="app.apps_research.c0.final_evidence_contract",
            accepted_emitter_categories=(),
            accepted_span_name_patterns=(),
            accepted_emitter_files=(),
            phase_a_status=ambiguous,
            required_attributes=_std_attrs(),
            live_trace_required=False,  # offender
            failure_conditions=("span missing",),
        )


def test_ambiguous_phase_a_status_allowed_when_live_trace_required_true() -> None:
    binding = ContractSpanBinding(
        contract_name="FinalEvidenceContract",
        normalized_cert_alias="app.apps_research.c0.final_evidence_contract",
        accepted_emitter_categories=(),
        accepted_span_name_patterns=(),
        accepted_emitter_files=(),
        phase_a_status=PhaseAStatus.UNKNOWN_NEEDS_RUNTIME_RUN,
        required_attributes=_std_attrs(),
        live_trace_required=True,
        failure_conditions=("span missing",),
    )
    assert binding.live_trace_required is True


# ---------------------------------------------------------------------------
# normalized_cert_alias rule
# ---------------------------------------------------------------------------


def test_normalized_cert_alias_must_be_nonempty() -> None:
    with pytest.raises(ValueError, match="normalized_cert_alias must be non-empty"):
        ContractSpanBinding(
            contract_name="ValidatedRequest",
            normalized_cert_alias="",  # offender
            accepted_emitter_categories=("L5.ingress.telemetry",),
            accepted_span_name_patterns=("ingress.*",),
            accepted_emitter_files=(),
            phase_a_status=PhaseAStatus.EXISTS_NAME_MISMATCH,
            required_attributes=_std_attrs(),
            live_trace_required=False,
            failure_conditions=("span missing",),
        )


# ---------------------------------------------------------------------------
# Basic required-field rules
# ---------------------------------------------------------------------------


def test_contract_name_must_be_nonempty() -> None:
    with pytest.raises(ValueError, match="contract_name must be non-empty"):
        ContractSpanBinding(
            contract_name="",  # offender
            normalized_cert_alias="app.apps_research.foo",
            accepted_emitter_categories=("X",),
            accepted_span_name_patterns=("x.*",),
            accepted_emitter_files=(),
            phase_a_status=PhaseAStatus.EXISTS_MATCHES_MATRIX,
            required_attributes=_std_attrs(),
            live_trace_required=False,
            failure_conditions=("span missing",),
        )


def test_app_name_must_start_with_apps_() -> None:
    with pytest.raises(ValueError, match="must be an apps_\\* directory name"):
        build_r3_grounded_read_contract(
            app_name="notapps_foo",
            manifest_path="notapps_foo/spine_manifest.yaml",
            manifest_hash="",
        )


def test_required_attribute_fields_must_be_nonempty() -> None:
    with pytest.raises(ValueError, match="name must be non-empty"):
        RequiredAttribute(
            name="",
            required=True,
            description="x",
            failure_if_missing="y",
        )


# ---------------------------------------------------------------------------
# Serialization round-trip
# ---------------------------------------------------------------------------


def test_serialization_round_trip_r3() -> None:
    original = build_r3_grounded_read_contract(
        app_name="apps_exec",
        manifest_path="apps_exec/spine_manifest.yaml",
        manifest_hash="sha256:deadbeef",
    )
    data = original.to_dict()
    restored = AppRouteContract.from_dict(data)
    assert restored.app_name == original.app_name
    assert restored.route_shape == original.route_shape
    assert restored.required_contracts == original.required_contracts
    assert len(restored.bindings) == len(original.bindings)
    for orig_b, restored_b in zip(original.bindings, restored.bindings):
        assert orig_b.contract_name == restored_b.contract_name
        assert orig_b.normalized_cert_alias == restored_b.normalized_cert_alias
        assert orig_b.phase_a_status == restored_b.phase_a_status
        assert orig_b.live_trace_required == restored_b.live_trace_required
    assert restored.forbidden_contracts == original.forbidden_contracts


def test_serialization_round_trip_formal_exception() -> None:
    original = build_formal_exception_contract(
        app_name="apps_underwriting_ai",
        route_shape=RouteShape.core_adjacent_utility,
        manifest_path="apps_underwriting_ai/spine_manifest.yaml",
        manifest_hash="sha256:cafe",
        reason_code="regulatory_domain",
        compensating_controls=("CC-UW-01", "CC-UW-02", "CC-UW-03", "CC-UW-04"),
    )
    data = original.to_dict()
    restored = AppRouteContract.from_dict(data)
    assert restored.formal_exception_reason_code == "regulatory_domain"
    assert restored.compensating_controls == (
        "CC-UW-01",
        "CC-UW-02",
        "CC-UW-03",
        "CC-UW-04",
    )
    assert restored.required_contracts == ()
    assert restored.bindings == ()


def test_to_json_produces_valid_json() -> None:
    import json

    c = build_r3_grounded_read_contract(
        app_name="apps_rg",
        manifest_path="apps_rg/spine_manifest.yaml",
        manifest_hash="",
    )
    s = c.to_json()
    parsed = json.loads(s)  # must not raise
    assert parsed["app_name"] == "apps_rg"
    assert parsed["route_shape"] == "R3_grounded_read"
    assert parsed["certification_level"] == "STATIC_EVIDENCE"
    assert "CommitRequest" in parsed["forbidden_contracts"]


# ---------------------------------------------------------------------------
# No-runtime-certification invariant sanity checks
# ---------------------------------------------------------------------------


def test_every_factory_returns_STATIC_EVIDENCE_level() -> None:
    """Phase B.2 is schema-only. No factory may return TRACE_OBSERVED
    or higher -- that is reserved for Phase C+ harness code."""
    r3 = build_r3_grounded_read_contract("apps_research", "apps_research/spine_manifest.yaml", "")
    btc = build_build_time_compiler_contract(
        "apps_qna", "apps_qna/spine_manifest.yaml", ""
    )
    fx = build_formal_exception_contract(
        "apps_eval",
        RouteShape.evaluator_only,
        "apps_eval/spine_manifest.yaml",
        "",
        "evaluator_isolation",
        ("CC-EVAL-01", "CC-EVAL-02", "CC-EVAL-03", "CC-EVAL-04"),
    )
    for c in (r3, btc, fx):
        assert c.certification_level == CertificationLevel.STATIC_EVIDENCE, (
            f"{c.app_name}: factory returned {c.certification_level.value}; "
            "Phase B.2 is schema-only -- no certification may be claimed"
        )
