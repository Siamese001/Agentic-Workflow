"""Unit tests for Phase C.5 — formal-exception per-app evidence extractor.

All tests use synthetic ``NormalizedTraceRow`` fixtures and injected envs.
No live SQLite, no runtime ADG query, no filesystem I/O (manifest-hash
tests use a real temp file).

Test plan: task spec §10 (13 required tests)
"""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import pytest

from system_learning.runtime_adg.app_route_contracts import (
    AppRouteContract,
    RouteShape,
    build_formal_exception_contract,
    build_r3_grounded_read_contract,
)
from tools.runtime_cert.runtime_adg_query_adapter import NOT_CERTIFIED
from tools.runtime_cert.trace_row_normalizer import (
    EXISTS_MATCHES_MATRIX,
    NormalizedTraceRow,
)
from tools.runtime_cert.extractors.formal_exception_evidence import (
    FormalControlEvidence,
    FormalExceptionEvidenceReport,
    extract_formal_exception_evidence,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_MANIFEST_HASH = "f" * 64


# ---------------------------------------------------------------------------
# Fixture factories
# ---------------------------------------------------------------------------


def _eval_contract(
    compensating_controls: tuple[str, ...] = ("CC-EVAL-01", "CC-EVAL-02"),
) -> AppRouteContract:
    return build_formal_exception_contract(
        app_name="apps_eval",
        route_shape=RouteShape.evaluator_only,
        manifest_path="apps_eval/spine_manifest.yaml",
        manifest_hash=_MANIFEST_HASH,
        reason_code="evaluator_only",
        compensating_controls=compensating_controls,
    )


def _uw_contract(
    compensating_controls: tuple[str, ...] = ("CC-UW-01", "CC-UW-02"),
) -> AppRouteContract:
    return build_formal_exception_contract(
        app_name="apps_underwriting_ai",
        route_shape=RouteShape.evaluator_only,
        manifest_path="apps_underwriting_ai/spine_manifest.yaml",
        manifest_hash=_MANIFEST_HASH,
        reason_code="regulatory_domain",
        compensating_controls=compensating_controls,
    )


def _shared_contract(
    compensating_controls: tuple[str, ...] = (
        "CC-SHARED-01", "CC-SHARED-02", "CC-SHARED-03",
        "CC-SHARED-04", "CC-SHARED-05",
    ),
) -> AppRouteContract:
    return build_formal_exception_contract(
        app_name="apps_shared",
        route_shape=RouteShape.core_adjacent_utility,
        manifest_path="apps_shared/spine_manifest.yaml",
        manifest_hash=_MANIFEST_HASH,
        reason_code="shared_library_surface",
        compensating_controls=compensating_controls,
    )


def _nrow(
    app_name: str,
    contract_name: str | None = None,
    span_id: str = "s1",
    trace_id: str = "trace-1",
    parent_span_id: str | None = None,
    span_name: str = "test.span",
    route_shape: str = "evaluator_only",
    source_path: str | None = None,
    phase_c_status: str = EXISTS_MATCHES_MATRIX,
    attrs: dict[str, Any] | None = None,
) -> NormalizedTraceRow:
    return NormalizedTraceRow(
        app_name=app_name,
        route_shape=route_shape,
        trace_id=trace_id,
        span_id=span_id,
        parent_span_id=parent_span_id,
        span_name=span_name,
        timestamp=1_000_000,
        contract_name=contract_name,
        normalized_cert_alias=None,
        phase_c_status=phase_c_status,
        match_basis="P3:test",
        mapping_notes="",
        binding_contract_name=contract_name,
        manifest_hash=_MANIFEST_HASH,
        static_runtime_mode="",
        runtime_certification_status=NOT_CERTIFIED,
        artifact_id=None,
        contract_id=None,
        source_path=source_path,
        attributes=attrs or {},
        evidence_source="runtime_adg.snapshot.test",
    )


# ---------------------------------------------------------------------------
# T1 — apps_eval passes on implemented controls; report stays NOT_CERTIFIED
# ---------------------------------------------------------------------------


def test_apps_eval_passes_when_no_circularity_and_no_leak():
    """T1: clean apps_eval rows pass CC-EVAL-01 + CC-EVAL-02; NOT_CERTIFIED held."""
    rows = [
        _nrow("apps_eval", span_id="root", parent_span_id=None,
              span_name="eval_stability", route_shape="evaluator_only"),
    ]
    report = extract_formal_exception_evidence(rows, _eval_contract())

    assert report.runtime_certification_status == NOT_CERTIFIED
    assert report.passed_formal_exception_observed is True
    assert report.missing_controls == ()
    assert report.failed_controls == ()
    assert {c.control_id for c in report.controls_evidence} == {"CC-EVAL-01", "CC-EVAL-02"}
    for c in report.controls_evidence:
        assert c.observed is True
        assert c.passed is True


def test_apps_eval_with_unimplemented_control_listed_reports_missing():
    """T1b: adding CC-EVAL-99 to the manifest lists it in missing_controls."""
    rows = [_nrow("apps_eval", span_id="root", parent_span_id=None,
                  span_name="eval_stability", route_shape="evaluator_only")]
    contract = _eval_contract(compensating_controls=("CC-EVAL-01", "CC-EVAL-02", "CC-EVAL-99"))
    report = extract_formal_exception_evidence(rows, contract)

    assert "CC-EVAL-99" in report.missing_controls
    assert report.passed_formal_exception_observed is False


# ---------------------------------------------------------------------------
# T2 — apps_eval fails on evaluator-of-evaluator circularity
# ---------------------------------------------------------------------------


def test_apps_eval_fails_on_circularity():
    """T2: root=apps_eval + descendant=apps_eval → CC-EVAL-01 fails."""
    rows = [
        _nrow("apps_eval", span_id="root", parent_span_id=None,
              trace_id="t_circ", span_name="eval_root"),
        _nrow("apps_eval", span_id="child", parent_span_id="root",
              trace_id="t_circ", span_name="eval_child_of_eval"),
    ]
    report = extract_formal_exception_evidence(rows, _eval_contract())

    cc01 = next(c for c in report.controls_evidence if c.control_id == "CC-EVAL-01")
    assert cc01.passed is False
    assert cc01.violation_count >= 1
    assert "CC-EVAL-01" in report.failed_controls
    assert report.passed_formal_exception_observed is False
    assert report.runtime_certification_status == NOT_CERTIFIED


# ---------------------------------------------------------------------------
# T3 — apps_eval fails on R3-contract leak
# ---------------------------------------------------------------------------


def test_apps_eval_fails_on_r3_leak():
    """T3: apps_eval row carrying SealedArtifact on a non-allowed surface fails."""
    rows = [
        _nrow("apps_eval", span_id="root", parent_span_id=None,
              span_name="eval_root", route_shape="evaluator_only"),
        _nrow("apps_eval", contract_name="SealedArtifact", span_id="leak",
              parent_span_id="root", span_name="not_allowed_surface",
              route_shape="some_other_surface"),
    ]
    report = extract_formal_exception_evidence(rows, _eval_contract())

    cc02 = next(c for c in report.controls_evidence if c.control_id == "CC-EVAL-02")
    assert cc02.passed is False
    assert cc02.violation_count >= 1
    assert "CC-EVAL-02" in report.failed_controls
    assert report.passed_formal_exception_observed is False


# ---------------------------------------------------------------------------
# T4 — apps_underwriting_ai fails on R3 leak
# ---------------------------------------------------------------------------


def test_apps_underwriting_fails_on_r3_leak():
    """T4: apps_underwriting_ai row with R3 contract on non-regulated surface fails."""
    rows = [
        _nrow("apps_underwriting_ai", contract_name="SealedArtifact",
              span_id="uw_leak", parent_span_id=None,
              span_name="leak_surface", route_shape="free_text_prose"),
    ]
    contract = _uw_contract(compensating_controls=("CC-UW-02",))
    report = extract_formal_exception_evidence(rows, contract)

    cc_uw2 = next(c for c in report.controls_evidence if c.control_id == "CC-UW-02")
    assert cc_uw2.passed is False
    assert "CC-UW-02" in report.failed_controls
    assert report.runtime_certification_status == NOT_CERTIFIED


# ---------------------------------------------------------------------------
# T5 — apps_underwriting_ai CC-UW-01 marked missing (no helper)
# ---------------------------------------------------------------------------


def test_apps_underwriting_cc_uw_01_marked_missing():
    """T5: CC-UW-01 listed but no helper → missing_controls, observed=False."""
    rows = [
        _nrow("apps_underwriting_ai", span_id="s1", parent_span_id=None,
              span_name="regulated_decision", route_shape="regulated_decision"),
    ]
    report = extract_formal_exception_evidence(rows, _uw_contract())

    assert "CC-UW-01" in report.missing_controls
    cc_uw1 = next(c for c in report.controls_evidence if c.control_id == "CC-UW-01")
    assert cc_uw1.observed is False
    assert cc_uw1.passed is False
    # Note explains why
    assert "not implemented" in cc_uw1.notes.lower() or \
           "positive regulated-decision" in cc_uw1.notes.lower()
    assert report.passed_formal_exception_observed is False


# ---------------------------------------------------------------------------
# T6 — apps_shared runs CC-SHARED-03 and CC-SHARED-05
# ---------------------------------------------------------------------------


def test_apps_shared_runs_cc_shared_03_and_05():
    """T6: apps_shared with only CC-SHARED-03 and CC-SHARED-05 runs both helpers."""
    contract = _shared_contract(compensating_controls=("CC-SHARED-03", "CC-SHARED-05"))
    rows: list[NormalizedTraceRow] = []
    # Pass env explicitly to make CC-SHARED-05 deterministic.
    report = extract_formal_exception_evidence(
        rows, contract, cc_shared_env={"AGENTIC_CORE_STACK": "full"},
    )

    control_ids = {c.control_id for c in report.controls_evidence}
    assert control_ids == {"CC-SHARED-03", "CC-SHARED-05"}
    for c in report.controls_evidence:
        assert c.observed is True
    assert report.runtime_certification_status == NOT_CERTIFIED


# ---------------------------------------------------------------------------
# T7 — apps_shared fails if CC-SHARED-05 env is standalone / not full
# ---------------------------------------------------------------------------


def test_apps_shared_cc_shared_05_fails_when_env_standalone():
    """T7: AGENTIC_CORE_STACK=standalone → CC-SHARED-05 fails."""
    contract = _shared_contract(compensating_controls=("CC-SHARED-05",))
    report = extract_formal_exception_evidence(
        [], contract, cc_shared_env={"AGENTIC_CORE_STACK": "standalone"},
    )

    cc05 = next(c for c in report.controls_evidence if c.control_id == "CC-SHARED-05")
    assert cc05.observed is True
    assert cc05.passed is False
    assert cc05.failure_reasons  # non-empty
    assert "CC-SHARED-05" in report.failed_controls
    assert report.passed_formal_exception_observed is False


# ---------------------------------------------------------------------------
# T8 — apps_shared marks CC-SHARED-01/02/04 missing (static controls)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("static_ctrl", ["CC-SHARED-01", "CC-SHARED-02", "CC-SHARED-04"])
def test_apps_shared_static_controls_marked_missing(static_ctrl: str):
    """T8: static CC-SHARED-01/02/04 listed → missing_controls with honest note."""
    contract = _shared_contract(compensating_controls=(static_ctrl,))
    report = extract_formal_exception_evidence(
        [], contract, cc_shared_env={"AGENTIC_CORE_STACK": "full"},
    )

    assert static_ctrl in report.missing_controls
    rec = next(c for c in report.controls_evidence if c.control_id == static_ctrl)
    assert rec.observed is False
    assert rec.passed is False
    assert "static" in rec.notes.lower() or "not runtime-verifiable" in rec.notes.lower()


def test_apps_shared_full_manifest_lists_all_five_controls():
    """T8b: default apps_shared manifest (5 controls) produces mixed bucketing."""
    report = extract_formal_exception_evidence(
        [], _shared_contract(), cc_shared_env={"AGENTIC_CORE_STACK": "full"},
    )

    # CC-SHARED-01/02/04 are missing; CC-SHARED-03 + 05 are observed
    assert set(report.missing_controls) == {"CC-SHARED-01", "CC-SHARED-02", "CC-SHARED-04"}
    observed_ids = {c.control_id for c in report.controls_evidence if c.observed}
    assert "CC-SHARED-03" in observed_ids
    assert "CC-SHARED-05" in observed_ids
    assert report.passed_formal_exception_observed is False  # 3 unimplemented


# ---------------------------------------------------------------------------
# T9 — passed_formal_exception_observed only True when all listed controls
#       are implemented + passed
# ---------------------------------------------------------------------------


def test_passed_only_when_every_control_implemented_and_passing():
    """T9: listing an unimplemented control → passed=False even if others pass."""
    # apps_eval with a bogus extra control
    contract = _eval_contract(compensating_controls=("CC-EVAL-01", "CC-EVAL-02", "CC-XX-99"))
    rows = [_nrow("apps_eval", span_id="root", parent_span_id=None,
                  span_name="eval_stability", route_shape="evaluator_only")]
    report = extract_formal_exception_evidence(rows, contract)

    assert report.passed_formal_exception_observed is False
    assert "CC-XX-99" in report.missing_controls


# ---------------------------------------------------------------------------
# T10 — runtime_certification_status always NOT_CERTIFIED
# ---------------------------------------------------------------------------


def test_runtime_certification_status_always_not_certified():
    """T10: even on a fully-passing apps_eval report, status stays NOT_CERTIFIED."""
    rows = [_nrow("apps_eval", span_id="root", parent_span_id=None,
                  span_name="eval_stability", route_shape="evaluator_only")]
    report = extract_formal_exception_evidence(rows, _eval_contract())

    assert report.runtime_certification_status == NOT_CERTIFIED
    assert report.passed_formal_exception_observed is True


def test_report_rejects_non_not_certified_status():
    """T10b: constructor __post_init__ rejects any other status."""
    with pytest.raises(ValueError, match="NOT_CERTIFIED"):
        FormalExceptionEvidenceReport(
            app_name="apps_eval",
            route_shape="evaluator_only",
            manifest_hash=_MANIFEST_HASH,
            static_runtime_mode="",
            formal_exception_reason_code="evaluator_only",
            compensating_controls=("CC-EVAL-01",),
            runtime_certification_status="FORMAL_EXCEPTION_VERIFIED",
            controls_evidence=(),
            missing_controls=(),
            failed_controls=(),
            passed_formal_exception_observed=False,
            failure_reasons=(),
            notes="",
        )


# ---------------------------------------------------------------------------
# T11 — invalid route shape rejected
# ---------------------------------------------------------------------------


def test_invalid_route_shape_raises():
    """T11: R3_grounded_read contract → extractor raises ValueError."""
    r3 = build_r3_grounded_read_contract(
        app_name="apps_research",
        manifest_path="apps_research/spine_manifest.yaml",
        manifest_hash="a" * 64,
    )
    with pytest.raises(ValueError, match="evaluator_only|core_adjacent_utility"):
        extract_formal_exception_evidence([], r3)


# ---------------------------------------------------------------------------
# T12 — empty compensating_controls rejected at contract-construction time
# ---------------------------------------------------------------------------


def test_empty_compensating_controls_rejected_by_factory():
    """T12: build_formal_exception_contract itself rejects empty list."""
    with pytest.raises(ValueError, match="compensating_controls"):
        build_formal_exception_contract(
            app_name="apps_eval",
            route_shape=RouteShape.evaluator_only,
            manifest_path="apps_eval/spine_manifest.yaml",
            manifest_hash=_MANIFEST_HASH,
            reason_code="evaluator_only",
            compensating_controls=(),
        )


def test_extractor_rejects_empty_compensating_controls_post_hoc():
    """T12b: if someone patches a contract to empty controls, extractor rejects."""
    contract_dict = _eval_contract().to_dict()
    contract_dict["compensating_controls"] = []
    # Bypass validation at construction with from_dict — but from_dict calls
    # __post_init__ too, which enforces the formal-exception invariant.
    # Instead: construct directly via dataclasses.replace on the built object.
    # We rely on the extractor's own check.
    # Skip this by verifying extractor rejects reason_code check path too:
    with pytest.raises(ValueError):
        # Construct by bypass: AppRouteContract accepts compensating_controls=()
        # when route_shape is R3 etc.  Use dataclasses.replace.
        import dataclasses as _dc
        c = _eval_contract()
        patched = _dc.replace(c, compensating_controls=())
        extract_formal_exception_evidence([], patched)


def test_extractor_rejects_empty_reason_code():
    """T12c: extractor rejects empty formal_exception_reason_code."""
    import dataclasses as _dc
    c = _eval_contract()
    patched = _dc.replace(c, formal_exception_reason_code="")
    with pytest.raises(ValueError, match="formal_exception_reason_code"):
        extract_formal_exception_evidence([], patched)


# ---------------------------------------------------------------------------
# T13 — serialization
# ---------------------------------------------------------------------------


def test_to_dict_serialisable():
    """T13: FormalExceptionEvidenceReport.to_dict() passes json.dumps."""
    rows = [_nrow("apps_eval", span_id="root", parent_span_id=None,
                  span_name="eval_stability", route_shape="evaluator_only")]
    report = extract_formal_exception_evidence(rows, _eval_contract())
    d = report.to_dict()
    j = json.dumps(d)
    assert "NOT_CERTIFIED" in j
    assert d["passed_formal_exception_observed"] is True


def test_to_json_round_trip():
    """T13b: to_json() parses back with expected top-level keys."""
    report = extract_formal_exception_evidence(
        [], _eval_contract(),
    )
    obj = json.loads(report.to_json())
    for key in (
        "app_name", "route_shape", "formal_exception_reason_code",
        "compensating_controls", "runtime_certification_status",
        "controls_evidence", "missing_controls", "failed_controls",
        "passed_formal_exception_observed",
    ):
        assert key in obj


def test_formal_control_evidence_to_dict_serialisable():
    """T13c: FormalControlEvidence.to_dict() passes json.dumps."""
    report = extract_formal_exception_evidence([], _shared_contract(),
                                                cc_shared_env={"AGENTIC_CORE_STACK": "full"})
    for c in report.controls_evidence:
        json.dumps(c.to_dict())


# ---------------------------------------------------------------------------
# T14 — rows from other apps preserved for circularity checks
# ---------------------------------------------------------------------------


def test_rows_from_other_apps_preserved_for_circularity():
    """T14: non-apps_eval rows still reach CC-EVAL-01 check (scan_summary counts them)."""
    rows = [
        _nrow("apps_eval", span_id="root1", parent_span_id=None,
              trace_id="t1", span_name="eval_root"),
        _nrow("apps_research", span_id="other1", parent_span_id=None,
              trace_id="t2", span_name="research_root"),
        _nrow("apps_shared", span_id="shared1", parent_span_id=None,
              trace_id="t3", span_name="shared_root"),
    ]
    report = extract_formal_exception_evidence(rows, _eval_contract())

    # CC-EVAL-01 should have seen all 3 traces (not just apps_eval).
    cc01 = next(c for c in report.controls_evidence if c.control_id == "CC-EVAL-01")
    assert cc01.observed is True
    # Passed because no apps_eval descendants are apps_eval
    assert cc01.passed is True


def test_circularity_check_uses_other_app_descendants():
    """T14b: apps_eval root with apps_other descendant → NOT a circularity."""
    rows = [
        _nrow("apps_eval", span_id="root", parent_span_id=None,
              trace_id="t1", span_name="eval_root"),
        _nrow("apps_shared", span_id="child", parent_span_id="root",
              trace_id="t1", span_name="shared_child"),
    ]
    report = extract_formal_exception_evidence(rows, _eval_contract())
    cc01 = next(c for c in report.controls_evidence if c.control_id == "CC-EVAL-01")
    assert cc01.passed is True


# ---------------------------------------------------------------------------
# Additional — manifest hash
# ---------------------------------------------------------------------------


def test_manifest_hash_computed_when_absent_and_path_exists():
    """manifest_hash auto-computed from real temp file when contract hash is empty."""
    with tempfile.NamedTemporaryFile(
        suffix=".yaml", delete=False, mode="w", encoding="utf-8"
    ) as f:
        f.write("app: apps_eval\ncompensating_controls:\n  - CC-EVAL-01\n")
        tmp_path = f.name

    try:
        expected = hashlib.sha256(Path(tmp_path).read_bytes()).hexdigest()
        contract_dict = _eval_contract().to_dict()
        contract_dict["manifest_hash"] = ""
        contract_dict["manifest_path"] = tmp_path
        contract_dict["certification_level"] = "STATIC_EVIDENCE"
        patched = AppRouteContract.from_dict(contract_dict)

        report = extract_formal_exception_evidence([], patched)
        assert report.manifest_hash == expected
        assert "computed at runtime" in report.notes
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_manifest_hash_used_directly_when_present():
    """manifest_hash from contract is preserved (no I/O)."""
    report = extract_formal_exception_evidence([], _eval_contract())
    assert report.manifest_hash == _MANIFEST_HASH


# ---------------------------------------------------------------------------
# Additional — FormalControlEvidence invariants
# ---------------------------------------------------------------------------


def test_formal_control_evidence_rejects_fake_pass():
    """observed=False + passed=True is a fake-pass — constructor must reject."""
    with pytest.raises(ValueError, match="fake-pass"):
        FormalControlEvidence(
            control_id="CC-TEST",
            observed=False,
            passed=True,
            violation_count=0,
            violations=(),
            failure_reasons=(),
            notes="",
        )


def test_formal_control_evidence_violation_count_mismatch_rejected():
    """violation_count must match len(violations)."""
    with pytest.raises(ValueError, match="violation_count"):
        FormalControlEvidence(
            control_id="CC-TEST",
            observed=True,
            passed=False,
            violation_count=5,
            violations=({"x": 1},),  # only 1 but count says 5
            failure_reasons=(),
            notes="",
        )


def test_unknown_app_produces_all_missing():
    """App with no implemented helpers → all controls listed in missing."""
    contract = build_formal_exception_contract(
        app_name="apps_hypothetical",
        route_shape=RouteShape.core_adjacent_utility,
        manifest_path="apps_hypothetical/spine_manifest.yaml",
        manifest_hash=_MANIFEST_HASH,
        reason_code="exploration",
        compensating_controls=("CC-HYPO-01",),
    )
    report = extract_formal_exception_evidence([], contract)
    assert "CC-HYPO-01" in report.missing_controls
    assert report.passed_formal_exception_observed is False
    assert "no implemented formal-exception helpers" in report.notes


def test_failure_reasons_deduplicated():
    """failure_reasons at the report level are deduplicated."""
    report = extract_formal_exception_evidence(
        [], _shared_contract(),
        cc_shared_env={"AGENTIC_CORE_STACK": "standalone"},
    )
    assert len(report.failure_reasons) == len(set(report.failure_reasons))


def test_apps_name_prefix_enforced_by_contract():
    """AppRouteContract itself enforces apps_* prefix — extractor's check is defense-in-depth."""
    with pytest.raises(ValueError, match="apps_"):
        build_formal_exception_contract(
            app_name="not_apps_eval",
            route_shape=RouteShape.evaluator_only,
            manifest_path="foo/spine_manifest.yaml",
            manifest_hash=_MANIFEST_HASH,
            reason_code="evaluator_only",
            compensating_controls=("CC-EVAL-01",),
        )
