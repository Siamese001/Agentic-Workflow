"""Unit tests for Phase C.7 — attribute-hardening gap report.

All tests use synthetic ``NormalizedTraceRow`` fixtures and real contract
factories from ``system_learning.runtime_adg.app_route_contracts``. No
live SQLite, no runtime ADG query, no filesystem I/O for manifest hashes.

Test plan reference: task spec §9 (14 required tests)
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from system_learning.runtime_adg.app_route_contracts import (
    R3_GROUNDED_READ_CONTRACTS,
    build_r3_grounded_read_contract,
)
from tools.runtime_cert.runtime_adg_query_adapter import NOT_CERTIFIED
from tools.runtime_cert.trace_row_normalizer import (
    ATTRIBUTE_HARDENING_REQUIRED,
    EXISTS_MATCHES_MATRIX,
    EXISTS_NAME_MISMATCH,
    FORBIDDEN_SPAN_VIOLATION,
    LEDGER_EVENT_ONLY,
    NormalizedTraceRow,
    STUB_ONLY,
    TELEMETRY_MARKER_ONLY,
    UNKNOWN_NEEDS_RUNTIME_RUN,
)
from tools.runtime_cert.reports.attribute_hardening_gap import (
    AttributeGap,
    AttributeHardeningGapReport,
    GAP_FORBIDDEN_SPAN_VIOLATION,
    GAP_LEDGER_EVENT_ONLY,
    GAP_MISSING_CONTRACT,
    GAP_MISSING_REQUIRED_ATTRIBUTE,
    GAP_NAME_MISMATCH,
    GAP_STUB_ONLY,
    GAP_TELEMETRY_MARKER_ONLY,
    GAP_UNKNOWN_NEEDS_RUNTIME_RUN,
    SEVERITY_CRITICAL,
    SEVERITY_HIGH,
    SEVERITY_INFO,
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
    build_attribute_hardening_gap_report,
)

# ---------------------------------------------------------------------------
# Constants / fixtures
# ---------------------------------------------------------------------------

_HASH = "a" * 64
_APP = "apps_research"


def _r3_contract(app_name: str = _APP) -> Any:
    return build_r3_grounded_read_contract(
        app_name=app_name,
        manifest_path=f"{app_name}/spine_manifest.yaml",
        manifest_hash=_HASH,
    )


def _row(
    *,
    app_name: str = _APP,
    contract_name: str | None,
    phase_c_status: str,
    span_id: str = "s1",
    span_name: str = "test.span",
    mapping_notes: str = "",
    normalized_cert_alias: str | None = None,
    route_shape: str = "R3_grounded_read",
    source_path: str | None = None,
    attrs: dict[str, Any] | None = None,
) -> NormalizedTraceRow:
    return NormalizedTraceRow(
        app_name=app_name,
        route_shape=route_shape,
        trace_id="trace-test",
        span_id=span_id,
        parent_span_id=None,
        span_name=span_name,
        timestamp=1_000_000,
        contract_name=contract_name,
        normalized_cert_alias=normalized_cert_alias,
        phase_c_status=phase_c_status,
        match_basis="P3:test",
        mapping_notes=mapping_notes,
        binding_contract_name=contract_name,
        manifest_hash=_HASH,
        static_runtime_mode="",
        runtime_certification_status=NOT_CERTIFIED,
        artifact_id=None,
        contract_id=None,
        source_path=source_path,
        attributes=attrs or {},
        evidence_source="runtime_adg.snapshot.test",
    )


# ---------------------------------------------------------------------------
# T1 — missing required contract → CRITICAL MISSING_CONTRACT
# ---------------------------------------------------------------------------


def test_missing_required_contract_produces_critical_gap():
    """T1: no rows at all → one CRITICAL MISSING_CONTRACT gap per required contract."""
    contract = _r3_contract()
    report = build_attribute_hardening_gap_report([], contract)

    assert report.runtime_certification_status == NOT_CERTIFIED
    assert report.highest_severity == SEVERITY_CRITICAL
    assert set(report.missing_contracts) == set(R3_GROUNDED_READ_CONTRACTS)
    for g in report.gaps:
        assert g.gap_type == GAP_MISSING_CONTRACT
        assert g.severity == SEVERITY_CRITICAL
        assert "do not certify" in g.recommendation.lower()


def test_partial_missing_contract():
    """T1b: 7/8 contracts observed → one MISSING_CONTRACT CRITICAL gap for the 8th."""
    contract = _r3_contract()
    # Provide observed contracts directly
    observed = [c for c in R3_GROUNDED_READ_CONTRACTS if c != "ExitReviewPacket"]
    report = build_attribute_hardening_gap_report(
        [], contract, observed_contracts=observed
    )

    assert report.missing_contracts == ("ExitReviewPacket",)
    assert report.highest_severity == SEVERITY_CRITICAL
    assert len([g for g in report.gaps if g.gap_type == GAP_MISSING_CONTRACT]) == 1


# ---------------------------------------------------------------------------
# T2 — ATTRIBUTE_HARDENING_REQUIRED → HIGH
# ---------------------------------------------------------------------------


def test_attribute_hardening_required_creates_high_gap_with_missing_attrs():
    """T2: row with ATTRIBUTE_HARDENING_REQUIRED + parsed missing attrs."""
    rows = [
        _row(
            contract_name="SealedArtifact",
            phase_c_status=ATTRIBUTE_HARDENING_REQUIRED,
            span_name="l2.step.seal",
            mapping_notes=(
                "Direct attribute assertion (post-hardening path).  "
                "Missing required attributes: ['run_id', 'contract_id']."
            ),
        ),
    ]
    contract = _r3_contract()
    report = build_attribute_hardening_gap_report(
        rows, contract, observed_contracts=R3_GROUNDED_READ_CONTRACTS,
    )

    hardening_gaps = [g for g in report.gaps if g.gap_type == GAP_MISSING_REQUIRED_ATTRIBUTE]
    assert len(hardening_gaps) == 1
    g = hardening_gaps[0]
    assert g.severity == SEVERITY_HIGH
    assert g.contract_name == "SealedArtifact"
    assert set(g.missing_attributes) == {"run_id", "contract_id"}
    assert g.row_count == 1
    assert "run_id" in g.recommendation
    assert "contract_id" in g.recommendation
    assert "SealedArtifact" in report.attribute_hardening_required
    assert "SealedArtifact" in report.blocked_contracts


def test_multiple_hardening_rows_aggregated():
    """T2b: multiple hardening rows for same contract are aggregated."""
    rows = [
        _row(
            contract_name="SealedArtifact",
            phase_c_status=ATTRIBUTE_HARDENING_REQUIRED,
            span_id=f"s{i}",
            span_name=f"l2.step.seal.{i}",
            mapping_notes=(
                f"Missing required attributes: ['attr_{i}', 'run_id']."
            ),
        )
        for i in range(3)
    ]
    report = build_attribute_hardening_gap_report(
        rows, _r3_contract(), observed_contracts=R3_GROUNDED_READ_CONTRACTS,
    )

    hardening = [g for g in report.gaps if g.gap_type == GAP_MISSING_REQUIRED_ATTRIBUTE]
    assert len(hardening) == 1
    assert hardening[0].row_count == 3
    assert {"run_id", "attr_0", "attr_1", "attr_2"} <= set(hardening[0].missing_attributes)


# ---------------------------------------------------------------------------
# T3 — UNKNOWN_NEEDS_RUNTIME_RUN → HIGH
# ---------------------------------------------------------------------------


def test_unknown_needs_runtime_run_creates_high_gap():
    """T3: UNKNOWN_NEEDS_RUNTIME_RUN row → HIGH gap + contract not marked missing."""
    rows = [
        _row(
            contract_name="FinalEvidenceContract",
            phase_c_status=UNKNOWN_NEEDS_RUNTIME_RUN,
            span_name="final.evidence",
        ),
    ]
    contract = _r3_contract()
    # Don't pass observed_contracts — let the extractor derive from rows.
    report = build_attribute_hardening_gap_report(rows, contract)

    unknown_gaps = [g for g in report.gaps if g.gap_type == GAP_UNKNOWN_NEEDS_RUNTIME_RUN]
    assert len(unknown_gaps) == 1
    assert unknown_gaps[0].severity == SEVERITY_HIGH
    assert unknown_gaps[0].contract_name == "FinalEvidenceContract"
    assert "Run live trace" in unknown_gaps[0].recommendation
    assert "FinalEvidenceContract" in report.unknown_needs_runtime_run
    # 7 other required contracts not in rows → missing; plus 1 HIGH unknown
    # FinalEvidenceContract is observed (has a row) so NOT in missing.
    assert "FinalEvidenceContract" not in report.missing_contracts
    assert len(report.missing_contracts) == 7


# ---------------------------------------------------------------------------
# T4 — CommitRequest on R3 → CRITICAL FORBIDDEN
# ---------------------------------------------------------------------------


def test_commit_request_produces_critical_forbidden_gap():
    """T4: FORBIDDEN_SPAN_VIOLATION row → CRITICAL gap."""
    rows = [
        _row(
            contract_name="CommitRequest",
            phase_c_status=FORBIDDEN_SPAN_VIOLATION,
            span_name="CommitRequest",
        ),
    ]
    report = build_attribute_hardening_gap_report(
        rows, _r3_contract(), observed_contracts=R3_GROUNDED_READ_CONTRACTS,
    )

    forbidden = [g for g in report.gaps if g.gap_type == GAP_FORBIDDEN_SPAN_VIOLATION]
    assert len(forbidden) == 1
    assert forbidden[0].severity == SEVERITY_CRITICAL
    assert "CommitRequest" in forbidden[0].contract_name
    assert "Remove forbidden span" in forbidden[0].recommendation
    assert "Author-Gate" in forbidden[0].recommendation
    assert "CommitRequest" in report.forbidden_violations
    assert report.highest_severity == SEVERITY_CRITICAL


# ---------------------------------------------------------------------------
# T5/T6/T7 — marker / ledger / stub → MEDIUM
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "status, expected_type",
    [
        (TELEMETRY_MARKER_ONLY, GAP_TELEMETRY_MARKER_ONLY),
        (LEDGER_EVENT_ONLY, GAP_LEDGER_EVENT_ONLY),
        (STUB_ONLY, GAP_STUB_ONLY),
    ],
)
def test_marker_ledger_stub_produce_medium_gaps(status: str, expected_type: str):
    """T5/T6/T7: marker / ledger / stub rows each produce a MEDIUM gap."""
    rows = [
        _row(
            contract_name="RouteContract",
            phase_c_status=status,
            span_name="marker.span",
        ),
    ]
    report = build_attribute_hardening_gap_report(
        rows, _r3_contract(), observed_contracts=R3_GROUNDED_READ_CONTRACTS,
    )

    match = [g for g in report.gaps if g.gap_type == expected_type]
    assert len(match) == 1
    assert match[0].severity == SEVERITY_MEDIUM
    assert "marker/stub" in match[0].recommendation
    assert match[0].contract_name == "RouteContract"


# ---------------------------------------------------------------------------
# T8 — PromptEnvelope satisfies CompiledPromptArtifact
# ---------------------------------------------------------------------------


def test_prompt_envelope_satisfies_compiled_prompt_artifact():
    """T8: PromptEnvelope-labeled row counts toward CompiledPromptArtifact."""
    rows = [
        _row(
            contract_name="PromptEnvelope",
            phase_c_status=EXISTS_MATCHES_MATRIX,
            span_name="prompt.envelope",
        ),
    ]
    contract = _r3_contract()
    report = build_attribute_hardening_gap_report(rows, contract)

    # CompiledPromptArtifact should NOT be in missing_contracts.
    assert "CompiledPromptArtifact" not in report.missing_contracts
    assert "PromptEnvelope" not in report.missing_contracts


def test_prompt_envelope_gap_notes_raw_contract_name():
    """T8b: Equivalent raw contract_name is noted when PromptEnvelope triggers a gap."""
    rows = [
        _row(
            contract_name="PromptEnvelope",
            phase_c_status=ATTRIBUTE_HARDENING_REQUIRED,
            span_name="prompt.envelope",
            mapping_notes="Missing required attributes: ['run_id'].",
        ),
    ]
    contract = _r3_contract()
    report = build_attribute_hardening_gap_report(
        rows, contract, observed_contracts=R3_GROUNDED_READ_CONTRACTS,
    )

    hardening = [g for g in report.gaps if g.gap_type == GAP_MISSING_REQUIRED_ATTRIBUTE]
    assert len(hardening) == 1
    g = hardening[0]
    assert g.contract_name == "CompiledPromptArtifact"  # canonicalized
    assert "PromptEnvelope" in g.notes


# ---------------------------------------------------------------------------
# T9 — rows from other apps ignored
# ---------------------------------------------------------------------------


def test_rows_from_other_apps_ignored():
    """T9: rows with app_name != contract.app_name → counted in notes, no gap."""
    rows = [
        _row(
            app_name="apps_other",
            contract_name="SealedArtifact",
            phase_c_status=FORBIDDEN_SPAN_VIOLATION,
            span_name="other.app.commit",
        ),
    ]
    report = build_attribute_hardening_gap_report(
        rows, _r3_contract(), observed_contracts=R3_GROUNDED_READ_CONTRACTS,
    )

    # No gap from the other-app row
    assert not any(g.app_name == "apps_other" for g in report.gaps)
    assert report.forbidden_violations == ()
    assert "apps_other" in report.notes


# ---------------------------------------------------------------------------
# T10 — no gaps → still NOT_CERTIFIED + highest_severity=INFO
# ---------------------------------------------------------------------------


def test_no_gaps_still_not_certified():
    """T10: when observed_contracts covers all + no problematic rows → INFO."""
    rows = [
        _row(
            contract_name="SealedArtifact",
            phase_c_status=EXISTS_MATCHES_MATRIX,
            span_name="l2.step.seal",
        ),
    ]
    report = build_attribute_hardening_gap_report(
        rows, _r3_contract(), observed_contracts=R3_GROUNDED_READ_CONTRACTS,
    )

    assert report.gap_count == 0
    assert report.gaps == ()
    assert report.highest_severity == SEVERITY_INFO
    assert report.runtime_certification_status == NOT_CERTIFIED
    assert report.missing_contracts == ()
    assert "NOT_CERTIFIED" in report.notes


# ---------------------------------------------------------------------------
# T11 — highest_severity computed deterministically
# ---------------------------------------------------------------------------


def test_highest_severity_critical_beats_high():
    """T11: critical + high coexist → highest_severity = CRITICAL."""
    rows = [
        _row(
            contract_name="FinalEvidenceContract",
            phase_c_status=UNKNOWN_NEEDS_RUNTIME_RUN,
        ),
        _row(
            contract_name="CommitRequest",
            phase_c_status=FORBIDDEN_SPAN_VIOLATION,
            span_id="s2",
        ),
    ]
    report = build_attribute_hardening_gap_report(
        rows, _r3_contract(), observed_contracts=R3_GROUNDED_READ_CONTRACTS,
    )
    assert report.highest_severity == SEVERITY_CRITICAL


def test_highest_severity_high_beats_medium():
    """T11b: HIGH + MEDIUM coexist → highest_severity = HIGH."""
    rows = [
        _row(
            contract_name="RouteContract",
            phase_c_status=UNKNOWN_NEEDS_RUNTIME_RUN,
            span_id="s1",
        ),
        _row(
            contract_name="SealedArtifact",
            phase_c_status=TELEMETRY_MARKER_ONLY,
            span_id="s2",
        ),
    ]
    report = build_attribute_hardening_gap_report(
        rows, _r3_contract(), observed_contracts=R3_GROUNDED_READ_CONTRACTS,
    )
    assert report.highest_severity == SEVERITY_HIGH


def test_highest_severity_low_beats_info():
    """T11c: LOW alone (NAME_MISMATCH) → highest_severity = LOW."""
    rows = [
        _row(
            contract_name="RouteContract",
            phase_c_status=EXISTS_NAME_MISMATCH,
            span_id="s1",
        ),
    ]
    report = build_attribute_hardening_gap_report(
        rows, _r3_contract(), observed_contracts=R3_GROUNDED_READ_CONTRACTS,
    )
    assert report.highest_severity == SEVERITY_LOW


# ---------------------------------------------------------------------------
# T12 — recommendations deterministic
# ---------------------------------------------------------------------------


def test_recommendations_deterministic_ordering():
    """T12: repeated calls return identical recommendation strings + ordering."""
    rows = [
        _row(
            contract_name="SealedArtifact",
            phase_c_status=ATTRIBUTE_HARDENING_REQUIRED,
            mapping_notes="Missing required attributes: ['run_id'].",
            span_id="s1",
        ),
        _row(
            contract_name="RouteContract",
            phase_c_status=UNKNOWN_NEEDS_RUNTIME_RUN,
            span_id="s2",
        ),
    ]
    r1 = build_attribute_hardening_gap_report(
        rows, _r3_contract(), observed_contracts=R3_GROUNDED_READ_CONTRACTS,
    )
    r2 = build_attribute_hardening_gap_report(
        rows, _r3_contract(), observed_contracts=R3_GROUNDED_READ_CONTRACTS,
    )
    assert r1.recommendations == r2.recommendations
    assert tuple(g.recommendation for g in r1.gaps) == tuple(
        g.recommendation for g in r2.gaps
    )


def test_recommendations_deduplicated():
    """T12b: identical recommendations collapse to one entry."""
    # Two SealedArtifact rows with same missing-attr set → same recommendation
    rows = [
        _row(
            contract_name="SealedArtifact",
            phase_c_status=ATTRIBUTE_HARDENING_REQUIRED,
            mapping_notes="Missing required attributes: ['run_id'].",
            span_id="s1",
        ),
        _row(
            contract_name="SealedArtifact",
            phase_c_status=ATTRIBUTE_HARDENING_REQUIRED,
            mapping_notes="Missing required attributes: ['run_id'].",
            span_id="s2",
        ),
    ]
    report = build_attribute_hardening_gap_report(
        rows, _r3_contract(), observed_contracts=R3_GROUNDED_READ_CONTRACTS,
    )
    # Both rows aggregate into one gap → one unique recommendation
    assert len(report.recommendations) == len(set(report.recommendations))


# ---------------------------------------------------------------------------
# T13 — serialization (to_dict / to_json)
# ---------------------------------------------------------------------------


def test_report_to_dict_json_roundtrip():
    """T13: to_dict() produces JSON-serialisable output with all fields."""
    rows = [
        _row(
            contract_name="SealedArtifact",
            phase_c_status=ATTRIBUTE_HARDENING_REQUIRED,
            mapping_notes="Missing required attributes: ['run_id'].",
        ),
    ]
    report = build_attribute_hardening_gap_report(
        rows, _r3_contract(), observed_contracts=R3_GROUNDED_READ_CONTRACTS,
    )
    d = report.to_dict()
    # Must be JSON-serialisable
    serialized = json.dumps(d)
    assert "NOT_CERTIFIED" in serialized

    # Round-trip through to_json
    reparsed = json.loads(report.to_json())
    for key in (
        "app_name",
        "route_shape",
        "runtime_certification_status",
        "gap_count",
        "gaps",
        "highest_severity",
        "blocked_contracts",
        "attribute_hardening_required",
        "unknown_needs_runtime_run",
        "forbidden_violations",
        "missing_contracts",
        "recommendations",
        "notes",
    ):
        assert key in reparsed


def test_gap_to_dict_json_serialisable():
    """T13b: AttributeGap.to_dict() is JSON-serialisable."""
    rows = [
        _row(
            contract_name="SealedArtifact",
            phase_c_status=ATTRIBUTE_HARDENING_REQUIRED,
            mapping_notes="Missing required attributes: ['run_id'].",
        ),
    ]
    report = build_attribute_hardening_gap_report(
        rows, _r3_contract(), observed_contracts=R3_GROUNDED_READ_CONTRACTS,
    )
    for g in report.gaps:
        json.dumps(g.to_dict())


# ---------------------------------------------------------------------------
# T14 — runtime_certification_status invariant
# ---------------------------------------------------------------------------


def test_report_rejects_non_not_certified_status():
    """T14: report constructor rejects any status other than NOT_CERTIFIED."""
    with pytest.raises(ValueError, match="NOT_CERTIFIED"):
        AttributeHardeningGapReport(
            app_name=_APP,
            route_shape="R3_grounded_read",
            manifest_hash=_HASH,
            static_runtime_mode="",
            runtime_certification_status="RUNTIME_CERTIFIED",
            gap_count=0,
            gaps=(),
            highest_severity=SEVERITY_INFO,
            blocked_contracts=(),
            attribute_hardening_required=(),
            unknown_needs_runtime_run=(),
            forbidden_violations=(),
            missing_contracts=(),
            recommendations=(),
            notes="",
        )


def test_gap_rejects_bad_gap_type():
    """AttributeGap.__post_init__ rejects unknown gap_type."""
    with pytest.raises(ValueError, match="gap_type"):
        AttributeGap(
            app_name=_APP,
            route_shape="R3_grounded_read",
            contract_name="X",
            normalized_cert_alias=None,
            gap_type="NONSENSE",
            severity=SEVERITY_HIGH,
            row_count=0,
            missing_attributes=(),
            observed_statuses=(),
            sample_span_names=(),
            sample_source_paths=(),
            recommendation="",
            notes="",
        )


def test_gap_rejects_bad_severity():
    """AttributeGap.__post_init__ rejects unknown severity."""
    with pytest.raises(ValueError, match="severity"):
        AttributeGap(
            app_name=_APP,
            route_shape="R3_grounded_read",
            contract_name="X",
            normalized_cert_alias=None,
            gap_type=GAP_MISSING_CONTRACT,
            severity="MEGA_CRITICAL",
            row_count=0,
            missing_attributes=(),
            observed_statuses=(),
            sample_span_names=(),
            sample_source_paths=(),
            recommendation="",
            notes="",
        )


def test_gap_rejects_negative_row_count():
    """AttributeGap.__post_init__ rejects row_count < 0."""
    with pytest.raises(ValueError, match="row_count"):
        AttributeGap(
            app_name=_APP,
            route_shape="R3_grounded_read",
            contract_name="X",
            normalized_cert_alias=None,
            gap_type=GAP_MISSING_CONTRACT,
            severity=SEVERITY_CRITICAL,
            row_count=-1,
            missing_attributes=(),
            observed_statuses=(),
            sample_span_names=(),
            sample_source_paths=(),
            recommendation="",
            notes="",
        )


def test_report_rejects_mismatched_gap_count():
    """AttributeHardeningGapReport.__post_init__ rejects gap_count != len(gaps)."""
    bad_gap = AttributeGap(
        app_name=_APP,
        route_shape="R3_grounded_read",
        contract_name="X",
        normalized_cert_alias=None,
        gap_type=GAP_MISSING_CONTRACT,
        severity=SEVERITY_CRITICAL,
        row_count=0,
        missing_attributes=(),
        observed_statuses=(),
        sample_span_names=(),
        sample_source_paths=(),
        recommendation="",
        notes="",
    )
    with pytest.raises(ValueError, match="gap_count"):
        AttributeHardeningGapReport(
            app_name=_APP,
            route_shape="R3_grounded_read",
            manifest_hash=_HASH,
            static_runtime_mode="",
            runtime_certification_status=NOT_CERTIFIED,
            gap_count=5,  # mismatch with 1 gap
            gaps=(bad_gap,),
            highest_severity=SEVERITY_CRITICAL,
            blocked_contracts=(),
            attribute_hardening_required=(),
            unknown_needs_runtime_run=(),
            forbidden_violations=(),
            missing_contracts=(),
            recommendations=(),
            notes="",
        )


# ---------------------------------------------------------------------------
# Additional — gap ordering
# ---------------------------------------------------------------------------


def test_gaps_sorted_critical_first():
    """Report orders gaps by severity DESC, then gap_type, then contract_name."""
    rows = [
        _row(
            contract_name="SealedArtifact",
            phase_c_status=ATTRIBUTE_HARDENING_REQUIRED,
            mapping_notes="Missing required attributes: ['run_id'].",
            span_id="s1",
        ),
        _row(
            contract_name="CommitRequest",
            phase_c_status=FORBIDDEN_SPAN_VIOLATION,
            span_id="s2",
        ),
        _row(
            contract_name="RouteContract",
            phase_c_status=TELEMETRY_MARKER_ONLY,
            span_id="s3",
        ),
    ]
    report = build_attribute_hardening_gap_report(
        rows, _r3_contract(), observed_contracts=R3_GROUNDED_READ_CONTRACTS,
    )
    severities = [g.severity for g in report.gaps]
    # All CRITICAL before HIGH before MEDIUM
    assert severities == sorted(
        severities,
        key=lambda s: -{
            SEVERITY_CRITICAL: 4,
            SEVERITY_HIGH: 3,
            SEVERITY_MEDIUM: 2,
            SEVERITY_LOW: 1,
            SEVERITY_INFO: 0,
        }[s],
    )


def test_blocked_contracts_includes_critical_and_high():
    """blocked_contracts collects all CRITICAL + HIGH contract names."""
    rows = [
        _row(
            contract_name="SealedArtifact",
            phase_c_status=ATTRIBUTE_HARDENING_REQUIRED,
            mapping_notes="Missing required attributes: ['run_id'].",
            span_id="s1",
        ),
    ]
    contract = _r3_contract()
    report = build_attribute_hardening_gap_report(rows, contract)
    # SealedArtifact has a HIGH hardening gap; all other 7 R3 required
    # contracts have CRITICAL missing-contract gaps.
    assert "SealedArtifact" in report.blocked_contracts
    for c in R3_GROUNDED_READ_CONTRACTS:
        if c != "SealedArtifact":
            assert c in report.blocked_contracts


def test_unresolved_row_without_contract_still_handled():
    """A row with contract_name=None and a gap status gets bucketed as (unresolved)."""
    rows = [
        _row(
            contract_name=None,
            phase_c_status=UNKNOWN_NEEDS_RUNTIME_RUN,
            span_name="unresolved.span",
        ),
    ]
    contract = _r3_contract()
    report = build_attribute_hardening_gap_report(rows, contract)
    # Row produces an UNKNOWN gap on "(unresolved)"
    unknown_gaps = [g for g in report.gaps if g.gap_type == GAP_UNKNOWN_NEEDS_RUNTIME_RUN]
    assert any(g.contract_name == "(unresolved)" for g in unknown_gaps)


def test_name_mismatch_single_row_produces_low_gap():
    """T11d: EXISTS_NAME_MISMATCH → LOW NAME_MISMATCH gap."""
    rows = [
        _row(
            contract_name="RouteContract",
            phase_c_status=EXISTS_NAME_MISMATCH,
            span_name="heal_router.custom_name",
        ),
    ]
    report = build_attribute_hardening_gap_report(
        rows, _r3_contract(), observed_contracts=R3_GROUNDED_READ_CONTRACTS,
    )
    name_gaps = [g for g in report.gaps if g.gap_type == GAP_NAME_MISMATCH]
    assert len(name_gaps) == 1
    assert name_gaps[0].severity == SEVERITY_LOW
    assert "canonical accepted pattern" in name_gaps[0].recommendation


def test_clean_row_produces_no_gap():
    """A clean EXISTS_MATCHES_MATRIX row produces no per-row gap."""
    rows = [
        _row(
            contract_name="SealedArtifact",
            phase_c_status=EXISTS_MATCHES_MATRIX,
            span_name="l2.step.seal",
        ),
    ]
    report = build_attribute_hardening_gap_report(
        rows, _r3_contract(), observed_contracts=R3_GROUNDED_READ_CONTRACTS,
    )
    # No gap from the clean row — only missing_contracts for the other 7
    per_row_gaps = [g for g in report.gaps if g.gap_type != GAP_MISSING_CONTRACT]
    assert per_row_gaps == []


def test_sample_span_names_capped():
    """Sample span names are capped at a reasonable number; excess noted."""
    rows = [
        _row(
            contract_name="SealedArtifact",
            phase_c_status=UNKNOWN_NEEDS_RUNTIME_RUN,
            span_id=f"s{i}",
            span_name=f"seal.span.{i}",
        )
        for i in range(10)
    ]
    report = build_attribute_hardening_gap_report(
        rows, _r3_contract(), observed_contracts=R3_GROUNDED_READ_CONTRACTS,
    )
    unknown = [g for g in report.gaps if g.gap_type == GAP_UNKNOWN_NEEDS_RUNTIME_RUN]
    assert len(unknown) == 1
    g = unknown[0]
    assert g.row_count == 10
    assert len(g.sample_span_names) <= 5
    assert "additional row" in g.notes


def test_observed_contracts_override_drops_other_observations():
    """When observed_contracts is passed explicitly, rows do NOT add more."""
    # PromptEnvelope row in data, but override says observed=['ValidatedRequest']
    rows = [
        _row(
            contract_name="PromptEnvelope",
            phase_c_status=EXISTS_MATCHES_MATRIX,
        ),
    ]
    contract = _r3_contract()
    report = build_attribute_hardening_gap_report(
        rows, contract, observed_contracts=["ValidatedRequest"],
    )
    # CompiledPromptArtifact NOT observed (override didn't include it)
    # → appears in missing_contracts even though a PromptEnvelope row exists
    assert "CompiledPromptArtifact" in report.missing_contracts
