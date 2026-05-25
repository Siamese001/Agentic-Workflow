"""Unit tests for Phase C.4 — build_time_compiler per-app evidence extractor.

All tests use synthetic ``NormalizedTraceRow`` and ``AppRouteContract``
fixtures. No live SQLite, no runtime ADG query. Manifest-hash tests use a
real temp file.

Test plan: task spec §7 (14 required tests)
"""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import pytest

from agentic_core.L6_system_learning.app_route_contracts import (
    AppRouteContract,
    BUILD_TIME_COMPILER_CONTRACTS,
    build_build_time_compiler_contract,
    build_r3_grounded_read_contract,
)
from tools.runtime_cert.runtime_adg_query_adapter import NOT_CERTIFIED
from tools.runtime_cert.trace_row_normalizer import (
    ATTRIBUTE_HARDENING_REQUIRED,
    EXISTS_MATCHES_MATRIX,
    FORBIDDEN_SPAN_VIOLATION,
    UNKNOWN_NEEDS_RUNTIME_RUN,
    NormalizedTraceRow,
)
from tools.runtime_cert.extractors.btc_evidence import (
    BTCContractEvidence,
    BTCEvidenceReport,
    extract_btc_evidence,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_APP = "apps_qna"
_MANIFEST_HASH = "q" * 64
_MANIFEST_PATH = "apps_qna/spine_manifest.yaml"

# The 3 canonical BTC contract names (matches BUILD_TIME_COMPILER_CONTRACTS)
_BTC_CONTRACTS = ("ValidatedRequest", "build.pack_artifact", "ledger.emit")

# R3-chain contracts forbidden on BTC apps (except ValidatedRequest, which
# is also in the BTC required set — carve-out applies).
_BTC_FORBIDDEN_R3 = (
    "L1PlanContract",
    "RouteContract",
    "RetrievalPlan",
    "FinalEvidenceContract",
    "CompiledPromptArtifact",
    "PromptEnvelope",
    "SealedArtifact",
    "ExitReviewPacket",
)


# ---------------------------------------------------------------------------
# Fixture factories
# ---------------------------------------------------------------------------


def _btc_contract(
    app_name: str = _APP,
    manifest_hash: str = _MANIFEST_HASH,
    manifest_path: str = _MANIFEST_PATH,
) -> AppRouteContract:
    return build_build_time_compiler_contract(
        app_name=app_name,
        manifest_path=manifest_path,
        manifest_hash=manifest_hash,
    )


def _nrow(
    contract_name: str | None,
    span_id: str = "s1",
    app_name: str = _APP,
    route_shape: str = "build_time_compiler",
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
        evidence_source="runtime_adg.snapshot.qna",
    )


def _all_btc_rows(app_name: str = _APP) -> list[NormalizedTraceRow]:
    """Return one clean observation row per BTC contract."""
    return [
        _nrow(c, span_id=f"s{i}", app_name=app_name)
        for i, c in enumerate(_BTC_CONTRACTS)
    ]


# ---------------------------------------------------------------------------
# T1 — complete BTC evidence → passed_trace_observed=True, NOT_CERTIFIED
# ---------------------------------------------------------------------------


def test_complete_btc_evidence_passes_and_stays_not_certified():
    """T1: all 3 BTC contracts observed → passed_trace_observed=True, NOT_CERTIFIED."""
    rows = _all_btc_rows()
    report = extract_btc_evidence(rows, _btc_contract())

    assert report.passed_trace_observed is True
    assert report.runtime_certification_status == NOT_CERTIFIED
    assert set(report.observed_contracts) == set(_BTC_CONTRACTS)
    assert report.missing_contracts == ()
    assert report.attribute_hardening_required == ()
    assert report.unknown_needs_runtime_run == ()
    assert report.forbidden_violations == ()


# ---------------------------------------------------------------------------
# T2 — missing build.pack_artifact
# ---------------------------------------------------------------------------


def test_missing_build_pack_artifact():
    """T2: omitting build.pack_artifact → in missing_contracts; passed=False."""
    rows = [r for r in _all_btc_rows() if r.contract_name != "build.pack_artifact"]
    report = extract_btc_evidence(rows, _btc_contract())

    assert "build.pack_artifact" in report.missing_contracts
    assert "build.pack_artifact" not in report.observed_contracts
    assert report.passed_trace_observed is False
    assert report.runtime_certification_status == NOT_CERTIFIED


# ---------------------------------------------------------------------------
# T3 — missing ledger.emit
# ---------------------------------------------------------------------------


def test_missing_ledger_emit():
    """T3: omitting ledger.emit → in missing_contracts; passed=False."""
    rows = [r for r in _all_btc_rows() if r.contract_name != "ledger.emit"]
    report = extract_btc_evidence(rows, _btc_contract())

    assert "ledger.emit" in report.missing_contracts
    assert report.passed_trace_observed is False


# ---------------------------------------------------------------------------
# T4 — forbidden R3 contract row for apps_qna → forbidden violation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("forbidden", _BTC_FORBIDDEN_R3)
def test_forbidden_r3_contract_produces_violation(forbidden: str):
    """T4: any R3-chain contract row on apps_qna → forbidden_violations entry."""
    rows = _all_btc_rows()
    rows.append(_nrow(forbidden, span_id=f"s_{forbidden}"))
    report = extract_btc_evidence(rows, _btc_contract())

    assert len(report.forbidden_violations) == 1
    assert report.forbidden_violations[0].contract_name == forbidden
    # Row preserved
    assert report.forbidden_violations[0].span_id == f"s_{forbidden}"
    assert report.passed_trace_observed is False
    assert report.runtime_certification_status == NOT_CERTIFIED


def test_prompt_envelope_is_forbidden_via_equivalence():
    """T4b: PromptEnvelope row triggers forbidden violation (equivalence)."""
    rows = _all_btc_rows()
    rows.append(_nrow("PromptEnvelope", span_id="s_pe"))
    report = extract_btc_evidence(rows, _btc_contract())

    assert len(report.forbidden_violations) == 1
    assert report.passed_trace_observed is False


# ---------------------------------------------------------------------------
# T5 — CommitRequest row for apps_qna → forbidden violation
# ---------------------------------------------------------------------------


def test_commit_request_produces_forbidden_violation():
    """T5: CommitRequest row on apps_qna → forbidden_violations."""
    rows = _all_btc_rows()
    commit_row = _nrow("CommitRequest", span_id="s_commit", span_name="CommitRequest")
    rows.append(commit_row)
    report = extract_btc_evidence(rows, _btc_contract())

    assert len(report.forbidden_violations) == 1
    assert report.forbidden_violations[0].span_id == "s_commit"
    assert report.passed_trace_observed is False


def test_commit_request_via_span_name_only():
    """T5b: row with span_name='CommitRequest' but no contract_name still flagged."""
    rows = _all_btc_rows()
    # contract_name=None, but span_name matches forbidden set
    rows.append(_nrow(None, span_id="s_raw_commit", span_name="CommitRequest"))
    report = extract_btc_evidence(rows, _btc_contract())

    assert len(report.forbidden_violations) == 1
    assert report.forbidden_violations[0].span_name == "CommitRequest"


# ---------------------------------------------------------------------------
# T6 — rows from other apps ignored
# ---------------------------------------------------------------------------


def test_rows_from_other_apps_ignored():
    """T6: rows with app_name != contract.app_name are ignored."""
    rows = _all_btc_rows()
    # Add rows from a different app, including forbidden contract names
    rows.append(_nrow("SealedArtifact", span_id="other_1", app_name="apps_research"))
    rows.append(_nrow("CommitRequest", span_id="other_2", app_name="apps_durable",
                      span_name="CommitRequest"))
    report = extract_btc_evidence(rows, _btc_contract())

    assert report.passed_trace_observed is True  # other-app rows do not contaminate
    assert report.forbidden_violations == ()
    assert "apps_research" in report.notes
    assert "apps_durable" in report.notes


# ---------------------------------------------------------------------------
# T7 — ATTRIBUTE_HARDENING_REQUIRED
# ---------------------------------------------------------------------------


def test_attribute_hardening_required_appears_in_report():
    """T7: ledger.emit with ATTRIBUTE_HARDENING_REQUIRED → in bucket."""
    rows = [r for r in _all_btc_rows() if r.contract_name != "ledger.emit"]
    rows.append(
        _nrow(
            "ledger.emit",
            span_id="s_led_hard",
            phase_c_status=ATTRIBUTE_HARDENING_REQUIRED,
            mapping_notes="Missing required attributes: manifest_hash, artifact_id.",
        )
    )
    report = extract_btc_evidence(rows, _btc_contract())

    assert "ledger.emit" in report.attribute_hardening_required
    assert "ledger.emit" not in report.observed_contracts
    assert report.passed_trace_observed is False

    ce = next(e for e in report.contract_evidence if e.contract_name == "ledger.emit")
    assert ("manifest_hash" in ce.missing_required_attributes
            or "artifact_id" in ce.missing_required_attributes)


# ---------------------------------------------------------------------------
# T8 — UNKNOWN_NEEDS_RUNTIME_RUN
# ---------------------------------------------------------------------------


def test_unknown_needs_runtime_run_appears_in_report():
    """T8: build.pack_artifact with UNKNOWN_NEEDS_RUNTIME_RUN → in bucket."""
    rows = [r for r in _all_btc_rows() if r.contract_name != "build.pack_artifact"]
    rows.append(
        _nrow(
            "build.pack_artifact",
            span_id="s_bp_unk",
            phase_c_status=UNKNOWN_NEEDS_RUNTIME_RUN,
        )
    )
    report = extract_btc_evidence(rows, _btc_contract())

    assert "build.pack_artifact" in report.unknown_needs_runtime_run
    assert report.passed_trace_observed is False


# ---------------------------------------------------------------------------
# T9 — manifest_hash computed when absent and path exists
# ---------------------------------------------------------------------------


def test_manifest_hash_computed_when_absent_and_path_exists():
    """T9: empty manifest_hash + valid path → hash computed, note emitted."""
    with tempfile.NamedTemporaryFile(
        suffix=".yaml", delete=False, mode="w", encoding="utf-8"
    ) as f:
        f.write("app: apps_qna\nversion: 1\n")
        tmp_path = f.name

    try:
        expected_hash = hashlib.sha256(Path(tmp_path).read_bytes()).hexdigest()

        contract_dict = _btc_contract().to_dict()
        contract_dict["manifest_hash"] = ""
        contract_dict["manifest_path"] = tmp_path
        contract_dict["certification_level"] = "STATIC_EVIDENCE"
        patched = AppRouteContract.from_dict(contract_dict)

        rows = _all_btc_rows()
        report = extract_btc_evidence(rows, patched)

        assert report.manifest_hash == expected_hash
        assert "computed at runtime" in report.notes
    finally:
        Path(tmp_path).unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# T10 — invalid route shape rejected
# ---------------------------------------------------------------------------


def test_invalid_route_shape_raises():
    """T10: contract with route_shape != build_time_compiler raises ValueError."""
    r3 = build_r3_grounded_read_contract(
        app_name="apps_research",
        manifest_path="apps_research/spine_manifest.yaml",
        manifest_hash="a" * 64,
    )
    with pytest.raises(ValueError, match="build_time_compiler"):
        extract_btc_evidence([], r3)


# ---------------------------------------------------------------------------
# T11 — empty rows → all missing
# ---------------------------------------------------------------------------


def test_empty_rows_produce_all_missing():
    """T11: no rows → all 3 BTC contracts in missing_contracts."""
    report = extract_btc_evidence([], _btc_contract())

    assert set(report.missing_contracts) == set(_BTC_CONTRACTS)
    assert report.observed_contracts == ()
    assert report.passed_trace_observed is False
    assert len(report.contract_evidence) == len(_BTC_CONTRACTS)
    assert all(not e.observed for e in report.contract_evidence)


# ---------------------------------------------------------------------------
# T12 — serialization
# ---------------------------------------------------------------------------


def test_to_dict_serialisable():
    """T12: BTCEvidenceReport.to_dict() passes json.dumps."""
    rows = _all_btc_rows()
    report = extract_btc_evidence(rows, _btc_contract())
    d = report.to_dict()
    j = json.dumps(d)
    assert "NOT_CERTIFIED" in j
    assert d["passed_trace_observed"] is True


def test_to_json_round_trip():
    """T12b: to_json() produces parseable JSON with expected keys."""
    report = extract_btc_evidence(_all_btc_rows(), _btc_contract())
    obj = json.loads(report.to_json())
    for key in (
        "app_name", "route_shape", "manifest_hash", "runtime_certification_status",
        "required_contracts", "observed_contracts", "missing_contracts",
        "passed_trace_observed", "contract_evidence",
    ):
        assert key in obj


def test_btc_contract_evidence_to_dict_serialisable():
    """T12c: BTCContractEvidence.to_dict() passes json.dumps."""
    rows = _all_btc_rows()
    report = extract_btc_evidence(rows, _btc_contract())
    ce = report.contract_evidence[0]
    json.dumps(ce.to_dict())


# ---------------------------------------------------------------------------
# T13 — input order does not matter
# ---------------------------------------------------------------------------


def test_input_order_does_not_matter():
    """T13: reversing row order produces identical evidence bucket sets."""
    rows_fwd = _all_btc_rows()
    rows_rev = list(reversed(rows_fwd))
    r_fwd = extract_btc_evidence(rows_fwd, _btc_contract())
    r_rev = extract_btc_evidence(rows_rev, _btc_contract())

    assert set(r_fwd.observed_contracts) == set(r_rev.observed_contracts)
    assert set(r_fwd.missing_contracts) == set(r_rev.missing_contracts)
    assert r_fwd.passed_trace_observed == r_rev.passed_trace_observed


# ---------------------------------------------------------------------------
# T14 — ValidatedRequest is allowed (carve-out from R3-chain forbidden set)
# ---------------------------------------------------------------------------


def test_validated_request_is_allowed_not_forbidden():
    """T14: ValidatedRequest is required, not forbidden, for BTC apps."""
    rows = _all_btc_rows()  # includes a ValidatedRequest row
    report = extract_btc_evidence(rows, _btc_contract())

    assert "ValidatedRequest" in report.observed_contracts
    assert report.forbidden_violations == ()
    assert report.passed_trace_observed is True


# ---------------------------------------------------------------------------
# Additional invariants
# ---------------------------------------------------------------------------


def test_btc_evidence_report_rejects_non_not_certified():
    """BTCEvidenceReport.__post_init__ raises on any non-NOT_CERTIFIED value."""
    with pytest.raises(ValueError, match="NOT_CERTIFIED"):
        BTCEvidenceReport(
            app_name=_APP,
            route_shape="build_time_compiler",
            manifest_hash=_MANIFEST_HASH,
            static_runtime_mode="",
            runtime_certification_status="RUNTIME_CERTIFIED",
            required_contracts=_BTC_CONTRACTS,
            observed_contracts=(),
            missing_contracts=_BTC_CONTRACTS,
            attribute_hardening_required=(),
            unknown_needs_runtime_run=(),
            forbidden_violations=(),
            contract_evidence=(),
            passed_trace_observed=False,
            failure_reasons=(),
            notes="",
        )


def test_manifest_hash_used_from_contract_directly():
    """manifest_hash from contract is used without I/O when present."""
    report = extract_btc_evidence(_all_btc_rows(), _btc_contract(manifest_hash=_MANIFEST_HASH))
    assert report.manifest_hash == _MANIFEST_HASH


def test_non_default_btc_app_gets_note():
    """contract.app_name != 'apps_qna' produces an informational note."""
    # Build a contract for a hypothetical other app (not apps_qna)
    other_contract = build_build_time_compiler_contract(
        app_name="apps_hypothetical",
        manifest_path="apps_hypothetical/spine_manifest.yaml",
        manifest_hash=_MANIFEST_HASH,
    )
    rows = _all_btc_rows(app_name="apps_hypothetical")
    report = extract_btc_evidence(rows, other_contract)
    assert "apps_qna" in report.notes or "apps_hypothetical" in report.notes


def test_multiple_rows_same_contract_all_collected():
    """Multiple rows for same BTC contract all captured."""
    rows = [r for r in _all_btc_rows() if r.contract_name != "build.pack_artifact"]
    for i in range(3):
        rows.append(_nrow("build.pack_artifact", span_id=f"bp_{i}",
                          artifact_id=f"pack-{i}"))
    report = extract_btc_evidence(rows, _btc_contract())
    ce = next(e for e in report.contract_evidence if e.contract_name == "build.pack_artifact")
    assert ce.row_count == 3
    assert ce.observed is True
    assert len(ce.artifact_ids) == 3


def test_forbidden_and_missing_simultaneously():
    """Forbidden R3 row + missing BTC contract both surface independently."""
    rows = [r for r in _all_btc_rows() if r.contract_name != "ledger.emit"]
    rows.append(_nrow("SealedArtifact", span_id="s_forbidden"))
    report = extract_btc_evidence(rows, _btc_contract())

    assert "ledger.emit" in report.missing_contracts
    assert len(report.forbidden_violations) == 1
    assert report.passed_trace_observed is False


def test_passed_false_when_forbidden_present_even_if_all_required_observed():
    """passed_trace_observed=False even if all 3 required observed, when forbidden row exists."""
    rows = _all_btc_rows()
    rows.append(_nrow("SealedArtifact", span_id="s_leak"))
    report = extract_btc_evidence(rows, _btc_contract())
    assert set(report.observed_contracts) == set(_BTC_CONTRACTS)
    assert report.passed_trace_observed is False


def test_c2_flagged_forbidden_row_preserved():
    """Row pre-flagged FORBIDDEN_SPAN_VIOLATION by C.2 is preserved as forbidden."""
    rows = _all_btc_rows()
    # Simulate a C.2-flagged row (e.g. from R3R4 path, shouldn't happen here
    # but must be preserved if present)
    rows.append(_nrow(
        "CommitRequest",
        span_id="s_c2_flagged",
        span_name="CommitRequest",
        phase_c_status=FORBIDDEN_SPAN_VIOLATION,
    ))
    report = extract_btc_evidence(rows, _btc_contract())
    assert len(report.forbidden_violations) == 1
    assert report.forbidden_violations[0].span_id == "s_c2_flagged"


def test_failure_reasons_deduplicated():
    """failure_reasons in BTCEvidenceReport are deduplicated."""
    report = extract_btc_evidence([], _btc_contract())
    assert len(report.failure_reasons) == len(set(report.failure_reasons))
