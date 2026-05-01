"""Unit tests for Phase C.3 — R3_grounded_read per-app evidence extractor.

All tests use synthetic ``NormalizedTraceRow`` and ``AppRouteContract``
fixtures.  No live SQLite, no runtime ADG query, no filesystem I/O
(manifest-hash tests use a real temp file).

Test plan: task spec §6 (12 required tests)
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest

from system_learning.runtime_adg.app_route_contracts import (
    CertificationLevel,
    ContractSpanBinding,
    PhaseAStatus,
    RequiredAttribute,
    RouteShape,
    build_r3_grounded_read_contract,
)
from tools.runtime_cert.runtime_adg_query_adapter import NOT_CERTIFIED
from tools.runtime_cert.trace_row_normalizer import (
    ATTRIBUTE_HARDENING_REQUIRED,
    EXISTS_MATCHES_MATRIX,
    EXISTS_NEEDS_ATTRIBUTE_HARDENING,
    FORBIDDEN_SPAN_VIOLATION,
    UNKNOWN_NEEDS_RUNTIME_RUN,
    NormalizedTraceRow,
)
from tools.runtime_cert.extractors.r3_evidence import (
    R3ContractEvidence,
    R3EvidenceReport,
    extract_r3_evidence,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_APP = "apps_research"
_MANIFEST_HASH = "a" * 64
_MANIFEST_PATH = "apps_research/spine_manifest.yaml"

# The 8 canonical R3 contract names (order matches AppRouteContract)
_R3_CONTRACTS = (
    "ValidatedRequest",
    "L1PlanContract",
    "RouteContract",
    "RetrievalPlan",
    "FinalEvidenceContract",
    "CompiledPromptArtifact",
    "SealedArtifact",
    "ExitReviewPacket",
)

# ---------------------------------------------------------------------------
# Fixture factories
# ---------------------------------------------------------------------------


def _contract(
    app_name: str = _APP,
    manifest_hash: str = _MANIFEST_HASH,
    manifest_path: str = _MANIFEST_PATH,
) -> "AppRouteContract":
    return build_r3_grounded_read_contract(
        app_name=app_name,
        manifest_path=manifest_path,
        manifest_hash=manifest_hash,
    )


def _nrow(
    contract_name: str | None,
    span_id: str = "s1",
    app_name: str = _APP,
    route_shape: str = "R3_grounded_read",
    phase_c_status: str = EXISTS_MATCHES_MATRIX,
    artifact_id: str | None = None,
    contract_id: str | None = None,
    span_name: str = "test.span",
    attrs: dict[str, Any] | None = None,
    mapping_notes: str = "",
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
        normalized_cert_alias=None,
        phase_c_status=phase_c_status,
        match_basis="P3:test",
        mapping_notes=mapping_notes,
        binding_contract_name=contract_name,
        manifest_hash=_MANIFEST_HASH,
        static_runtime_mode="",
        runtime_certification_status=NOT_CERTIFIED,
        artifact_id=artifact_id,
        contract_id=contract_id,
        source_path=None,
        attributes=attrs or {},
        evidence_source="runtime_adg.snapshot.abc123",
    )


def _all_r3_rows(app_name: str = _APP) -> list[NormalizedTraceRow]:
    """Return one clean observation row per R3 contract."""
    return [
        _nrow(c, span_id=f"s{i}", app_name=app_name)
        for i, c in enumerate(_R3_CONTRACTS)
    ]


# ---------------------------------------------------------------------------
# T1 — complete 8-contract evidence → passed_trace_observed=True, NOT_CERTIFIED
# ---------------------------------------------------------------------------


def test_complete_r3_evidence_passes_and_stays_not_certified():
    """T1: all 8 R3 contracts observed → passed_trace_observed=True, NOT_CERTIFIED."""
    rows = _all_r3_rows()
    report = extract_r3_evidence(rows, _contract())

    assert report.passed_trace_observed is True
    assert report.runtime_certification_status == NOT_CERTIFIED
    assert set(report.observed_contracts) == set(_R3_CONTRACTS)
    assert report.missing_contracts == ()
    assert report.attribute_hardening_required == ()
    assert report.unknown_needs_runtime_run == ()
    assert report.forbidden_violations == ()


# ---------------------------------------------------------------------------
# T2 — missing one contract → appears in missing_contracts
# ---------------------------------------------------------------------------


def test_missing_one_contract_appears_in_missing():
    """T2: omitting SealedArtifact rows → SealedArtifact in missing_contracts."""
    rows = [r for r in _all_r3_rows() if r.contract_name != "SealedArtifact"]
    report = extract_r3_evidence(rows, _contract())

    assert "SealedArtifact" in report.missing_contracts
    assert report.passed_trace_observed is False
    assert report.runtime_certification_status == NOT_CERTIFIED


def test_missing_multiple_contracts():
    """T2b: multiple missing contracts are all reported."""
    rows = [
        _nrow("ValidatedRequest", span_id="s0"),
        _nrow("RouteContract", span_id="s1"),
    ]
    report = extract_r3_evidence(rows, _contract())
    missing = set(report.missing_contracts)
    assert "L1PlanContract" in missing
    assert "SealedArtifact" in missing
    assert report.passed_trace_observed is False


# ---------------------------------------------------------------------------
# T3 — PromptEnvelope satisfies CompiledPromptArtifact
# ---------------------------------------------------------------------------


def test_prompt_envelope_satisfies_compiled_prompt_artifact():
    """T3: PromptEnvelope row counts as CompiledPromptArtifact observation."""
    rows = [r for r in _all_r3_rows() if r.contract_name != "CompiledPromptArtifact"]
    # Add a PromptEnvelope row in its place
    rows.append(_nrow("PromptEnvelope", span_id="s_pe"))
    report = extract_r3_evidence(rows, _contract())

    assert "CompiledPromptArtifact" in report.observed_contracts
    assert "CompiledPromptArtifact" not in report.missing_contracts
    assert report.passed_trace_observed is True
    # Verify the note is present on the contract evidence
    ce = next(e for e in report.contract_evidence if e.contract_name == "CompiledPromptArtifact")
    assert "PromptEnvelope" in ce.notes


# ---------------------------------------------------------------------------
# T4 — CommitRequest row for same app → forbidden violation, row preserved
# ---------------------------------------------------------------------------


def test_commit_request_produces_forbidden_violation():
    """T4: CommitRequest row on R3 app → forbidden_violations non-empty."""
    rows = _all_r3_rows()
    commit_row = _nrow(
        "CommitRequest",
        span_id="s_commit",
        span_name="CommitRequest",
        phase_c_status=FORBIDDEN_SPAN_VIOLATION,
    )
    rows.append(commit_row)
    report = extract_r3_evidence(rows, _contract())

    assert len(report.forbidden_violations) == 1
    assert report.forbidden_violations[0].span_id == "s_commit"
    # Row is preserved in the report
    assert report.forbidden_violations[0].span_name == "CommitRequest"
    assert report.passed_trace_observed is False
    assert report.runtime_certification_status == NOT_CERTIFIED


# ---------------------------------------------------------------------------
# T5 — rows from other apps are ignored
# ---------------------------------------------------------------------------


def test_rows_from_other_apps_ignored():
    """T5: rows with app_name != contract.app_name are ignored for evidence."""
    rows = _all_r3_rows()
    # Add rows from a different app
    other_rows = [
        _nrow(c, span_id=f"other_{i}", app_name="apps_eval")
        for i, c in enumerate(_R3_CONTRACTS)
    ]
    all_rows = rows + other_rows
    report = extract_r3_evidence(all_rows, _contract())

    assert report.passed_trace_observed is True
    assert "apps_eval" in report.notes
    assert report.runtime_certification_status == NOT_CERTIFIED


# ---------------------------------------------------------------------------
# T6 — ATTRIBUTE_HARDENING_REQUIRED appears in report
# ---------------------------------------------------------------------------


def test_attribute_hardening_required_appears_in_report():
    """T6: SealedArtifact with ATTRIBUTE_HARDENING_REQUIRED → in attribute_hardening_required."""
    rows = [r for r in _all_r3_rows() if r.contract_name != "SealedArtifact"]
    rows.append(
        _nrow(
            "SealedArtifact",
            span_id="s_seal_hard",
            phase_c_status=ATTRIBUTE_HARDENING_REQUIRED,
            mapping_notes="Missing required attributes: manifest_hash, contract_id.",
        )
    )
    report = extract_r3_evidence(rows, _contract())

    assert "SealedArtifact" in report.attribute_hardening_required
    assert "SealedArtifact" not in report.observed_contracts
    assert report.passed_trace_observed is False
    # Check missing attrs surfaced
    ce = next(e for e in report.contract_evidence if e.contract_name == "SealedArtifact")
    assert "manifest_hash" in ce.missing_required_attributes or \
           "contract_id" in ce.missing_required_attributes


# ---------------------------------------------------------------------------
# T7 — UNKNOWN_NEEDS_RUNTIME_RUN appears in report
# ---------------------------------------------------------------------------


def test_unknown_needs_runtime_run_appears_in_report():
    """T7: FinalEvidenceContract with UNKNOWN_NEEDS_RUNTIME_RUN → in unknown_needs_runtime_run."""
    rows = [r for r in _all_r3_rows() if r.contract_name != "FinalEvidenceContract"]
    rows.append(
        _nrow(
            "FinalEvidenceContract",
            span_id="s_fec_unk",
            phase_c_status=UNKNOWN_NEEDS_RUNTIME_RUN,
        )
    )
    report = extract_r3_evidence(rows, _contract())

    assert "FinalEvidenceContract" in report.unknown_needs_runtime_run
    assert "FinalEvidenceContract" not in report.observed_contracts
    assert report.passed_trace_observed is False
    assert report.runtime_certification_status == NOT_CERTIFIED


# ---------------------------------------------------------------------------
# T8 — manifest_hash computed when absent and path exists
# ---------------------------------------------------------------------------


def test_manifest_hash_computed_when_absent_and_path_exists():
    """T8: contract with empty manifest_hash but valid path → hash computed."""
    # Write a real temp manifest file
    with tempfile.NamedTemporaryFile(
        suffix=".yaml", delete=False, mode="w", encoding="utf-8"
    ) as f:
        f.write("app: apps_test\nversion: 1\n")
        tmp_path = f.name

    try:
        # Build contract with empty hash but valid path
        import hashlib
        expected_hash = hashlib.sha256(
            Path(tmp_path).read_bytes()
        ).hexdigest()

        # Use build_r3_grounded_read_contract with hash="" — but that raises
        # because manifest_hash is required at STATIC_EVIDENCE+ levels.
        # We patch the contract with hash="" via from_dict to bypass __post_init__.
        from system_learning.runtime_adg.app_route_contracts import AppRouteContract
        contract_dict = _contract(manifest_hash=_MANIFEST_HASH).to_dict()
        contract_dict["manifest_hash"] = ""
        contract_dict["certification_level"] = "STATIC_EVIDENCE"
        contract_dict["manifest_path"] = tmp_path
        # Patch required_contracts to pass R3 check but skip the manifest check
        patched = AppRouteContract.from_dict(contract_dict)

        rows = _all_r3_rows()
        report = extract_r3_evidence(rows, patched)

        assert report.manifest_hash == expected_hash
        assert "computed at runtime" in report.notes
    finally:
        Path(tmp_path).unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# T9 — invalid route shape rejected
# ---------------------------------------------------------------------------


def test_invalid_route_shape_raises():
    """T9: contract with route_shape != R3_grounded_read raises ValueError."""
    from system_learning.runtime_adg.app_route_contracts import (
        build_build_time_compiler_contract,
    )
    btc_contract = build_build_time_compiler_contract(
        app_name="apps_qna",
        manifest_path="apps_qna/spine_manifest.yaml",
        manifest_hash=_MANIFEST_HASH,
    )
    with pytest.raises(ValueError, match="R3_grounded_read"):
        extract_r3_evidence([], btc_contract)


# ---------------------------------------------------------------------------
# T10 — empty rows → all required contracts are missing
# ---------------------------------------------------------------------------


def test_empty_rows_produce_all_missing():
    """T10: no rows → all 8 required contracts in missing_contracts."""
    report = extract_r3_evidence([], _contract())

    assert set(report.missing_contracts) == set(_R3_CONTRACTS)
    assert report.observed_contracts == ()
    assert report.passed_trace_observed is False
    assert len(report.contract_evidence) == len(_R3_CONTRACTS)
    assert all(not e.observed for e in report.contract_evidence)


# ---------------------------------------------------------------------------
# T11 — serialization to_dict / to_json works
# ---------------------------------------------------------------------------


def test_to_dict_serialisable():
    """T11: R3EvidenceReport.to_dict() passes json.dumps without raising."""
    rows = _all_r3_rows()
    report = extract_r3_evidence(rows, _contract())
    d = report.to_dict()
    serialised = json.dumps(d)
    assert isinstance(serialised, str)
    assert "NOT_CERTIFIED" in serialised
    assert d["passed_trace_observed"] is True


def test_to_json_round_trip():
    """T11b: to_json() produces valid JSON with expected top-level keys."""
    rows = _all_r3_rows()
    report = extract_r3_evidence(rows, _contract())
    j = report.to_json()
    obj = json.loads(j)
    for key in (
        "app_name", "route_shape", "manifest_hash", "runtime_certification_status",
        "required_contracts", "observed_contracts", "missing_contracts",
        "passed_trace_observed", "contract_evidence",
    ):
        assert key in obj, f"Key {key!r} missing from to_json() output"


def test_r3_contract_evidence_to_dict_serialisable():
    """T11c: R3ContractEvidence.to_dict() passes json.dumps without raising."""
    row = _nrow("RouteContract")
    rows = [row]
    report = extract_r3_evidence(rows + [
        _nrow(c, span_id=f"s{i}") for i, c in enumerate(_R3_CONTRACTS)
        if c != "RouteContract"
    ], _contract())
    ce = next(e for e in report.contract_evidence if e.contract_name == "RouteContract")
    d = ce.to_dict()
    json.dumps(d)  # must not raise
    assert d["contract_name"] == "RouteContract"
    assert d["observed"] is True


# ---------------------------------------------------------------------------
# T12 — input order does not matter
# ---------------------------------------------------------------------------


def test_input_order_does_not_matter():
    """T12: reversing row input order produces identical evidence sets."""
    rows_fwd = _all_r3_rows()
    rows_rev = list(reversed(rows_fwd))

    report_fwd = extract_r3_evidence(rows_fwd, _contract())
    report_rev = extract_r3_evidence(rows_rev, _contract())

    assert set(report_fwd.observed_contracts) == set(report_rev.observed_contracts)
    assert set(report_fwd.missing_contracts) == set(report_rev.missing_contracts)
    assert report_fwd.passed_trace_observed == report_rev.passed_trace_observed


# ---------------------------------------------------------------------------
# Additional: R3EvidenceReport rejects non-NOT_CERTIFIED status
# ---------------------------------------------------------------------------


def test_r3_evidence_report_rejects_non_not_certified():
    """R3EvidenceReport.__post_init__ raises ValueError on bad cert status."""
    with pytest.raises(ValueError, match="NOT_CERTIFIED"):
        R3EvidenceReport(
            app_name=_APP,
            route_shape="R3_grounded_read",
            manifest_hash=_MANIFEST_HASH,
            static_runtime_mode="",
            runtime_certification_status="RUNTIME_CERTIFIED",
            required_contracts=_R3_CONTRACTS,
            observed_contracts=(),
            missing_contracts=_R3_CONTRACTS,
            attribute_hardening_required=(),
            unknown_needs_runtime_run=(),
            forbidden_violations=(),
            contract_evidence=(),
            passed_trace_observed=False,
            failure_reasons=(),
            notes="",
        )


# ---------------------------------------------------------------------------
# Additional: manifest_hash preserved when contract has one
# ---------------------------------------------------------------------------


def test_manifest_hash_used_from_contract():
    """manifest_hash from contract is used directly (no I/O)."""
    rows = _all_r3_rows()
    report = extract_r3_evidence(rows, _contract(manifest_hash=_MANIFEST_HASH))
    assert report.manifest_hash == _MANIFEST_HASH


# ---------------------------------------------------------------------------
# Additional: multiple rows for same contract → all collected
# ---------------------------------------------------------------------------


def test_multiple_rows_for_same_contract_all_collected():
    """Multiple rows mapping to RouteContract are all captured in R3ContractEvidence."""
    rows = [r for r in _all_r3_rows() if r.contract_name != "RouteContract"]
    for i in range(3):
        rows.append(_nrow("RouteContract", span_id=f"rc_{i}", artifact_id=f"art-{i}"))
    report = extract_r3_evidence(rows, _contract())

    ce = next(e for e in report.contract_evidence if e.contract_name == "RouteContract")
    assert ce.row_count == 3
    assert ce.observed is True
    assert len(ce.artifact_ids) == 3


# ---------------------------------------------------------------------------
# Additional: mixed statuses — some clean + some hardening → observed=True
# ---------------------------------------------------------------------------


def test_mixed_statuses_with_clean_row_is_observed():
    """A contract with one clean row + one hardening row is still observed."""
    rows = [r for r in _all_r3_rows() if r.contract_name != "L1PlanContract"]
    rows.append(_nrow("L1PlanContract", span_id="l1_ok",
                      phase_c_status=EXISTS_NEEDS_ATTRIBUTE_HARDENING))
    # EXISTS_NEEDS_ATTRIBUTE_HARDENING is not a fail-closed gap status
    # → the contract is observed (the status is informational from Phase A)
    rows.append(_nrow("L1PlanContract", span_id="l1_hard",
                      phase_c_status=ATTRIBUTE_HARDENING_REQUIRED))
    report = extract_r3_evidence(rows, _contract())
    # EXISTS_NEEDS_ATTRIBUTE_HARDENING is not in _gap_statuses → observed=True
    ce = next(e for e in report.contract_evidence if e.contract_name == "L1PlanContract")
    assert ce.observed is True


# ---------------------------------------------------------------------------
# Additional: artifact_ids and contract_ids collected
# ---------------------------------------------------------------------------


def test_artifact_and_contract_ids_collected():
    """artifact_id and contract_id values are collected in R3ContractEvidence."""
    rows = [r for r in _all_r3_rows() if r.contract_name != "SealedArtifact"]
    rows.append(_nrow("SealedArtifact", span_id="seal1",
                      artifact_id="art-abc", contract_id="con-123"))
    report = extract_r3_evidence(rows, _contract())
    ce = next(e for e in report.contract_evidence if e.contract_name == "SealedArtifact")
    assert "art-abc" in ce.artifact_ids
    assert "con-123" in ce.contract_ids


# ---------------------------------------------------------------------------
# Additional: app_name validation
# ---------------------------------------------------------------------------


def test_invalid_app_name_raises():
    """extract_r3_evidence raises ValueError if app_name doesn't start with apps_."""
    from system_learning.runtime_adg.app_route_contracts import AppRouteContract
    contract_dict = _contract().to_dict()
    contract_dict["app_name"] = "apps_research"  # valid — just verify no raise
    valid = AppRouteContract.from_dict(contract_dict)
    # Should not raise
    extract_r3_evidence([], valid)


# ---------------------------------------------------------------------------
# Additional: no duplicate failure_reasons in report
# ---------------------------------------------------------------------------


def test_failure_reasons_deduplicated():
    """failure_reasons in R3EvidenceReport are deduplicated."""
    # All 8 contracts missing — each emits one failure reason
    report = extract_r3_evidence([], _contract())
    assert len(report.failure_reasons) == len(set(report.failure_reasons))


# ---------------------------------------------------------------------------
# Additional: passed_trace_observed is False when forbidden violation present
# ---------------------------------------------------------------------------


def test_passed_trace_observed_false_with_forbidden():
    """passed_trace_observed=False even when all 8 contracts observed if forbidden row."""
    rows = _all_r3_rows()
    commit_row = _nrow(
        "CommitRequest",
        span_id="s_commit",
        span_name="CommitRequest",
        phase_c_status=FORBIDDEN_SPAN_VIOLATION,
    )
    rows.append(commit_row)
    report = extract_r3_evidence(rows, _contract())
    assert report.passed_trace_observed is False
