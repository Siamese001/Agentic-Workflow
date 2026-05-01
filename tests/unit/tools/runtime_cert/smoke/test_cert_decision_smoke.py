"""Unit tests for the Phase D.4 cert-decision smoke harness.

Every test uses ``tmp_path`` for ``repo_root``. No test writes to the
real ``artifacts/ledgers/`` tree. No test loads a live runtime-ADG
snapshot. No test parses Markdown. No app is certified. Every persisted
and read-back row carries ``runtime_certification_status = NOT_CERTIFIED``.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Iterable, Tuple

import pytest

from tools.runtime_cert.decisions.cert_decision_evaluator import (
    SAMPLE_SIZE_TOO_SMALL,
)
from tools.runtime_cert.decisions.cert_decision_ledger import (
    CertDecisionLedgerWriteResult,
    ledger_path_for_app,
)
from tools.runtime_cert.decisions.cert_decision_record import (
    EVIDENCE_KIND_BTC,
    EVIDENCE_KIND_R3,
    NOT_CERTIFIED,
    VERDICT_CERTIFY,
    VERDICT_HOLD,
    VERDICT_REJECT,
    CertificationDecisionRecord,
    make_certification_decision_record,
)
from tools.runtime_cert.reports.phase_c_closeout import (
    AppCloseoutSummary,
    PhaseCCloseoutReport,
    REPORT_DISCLAIMER,
)
from tools.runtime_cert.smoke import cert_decision_smoke as smoke
from tools.runtime_cert.smoke.cert_decision_smoke import (
    DECISION_COUNT_DOES_NOT_MATCH_INPUT,
    DISCLAIMER,
    LEDGER_WRITE_SKIPPED,
    MISSING_READBACK,
    SCHEMA_VERSION,
    SMOKE_FAILURE_REASONS,
    CertDecisionSmokeReport,
    run_cert_decision_smoke,
    write_cert_decision_smoke_report,
)


# ---------------------------------------------------------------------------
# Fixture helpers — follow the pattern used by test_cert_decision_evaluator.
# ---------------------------------------------------------------------------


def _h(seed: str) -> str:
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


MANIFEST_A = _h("manifest-smoke-A")
MANIFEST_B = _h("manifest-smoke-B")
MANIFEST_C = _h("manifest-smoke-C")
GEN_AT = "2026-05-01T12:00:00Z"


def _summary(
    *,
    app_name: str = "apps_research",
    evidence_kind: str = EVIDENCE_KIND_R3,
    manifest_hash: str = MANIFEST_A,
    passed_trace_observed: bool = False,
    passed_formal_exception_observed: bool = False,
    missing_contracts: Tuple[str, ...] = (),
    forbidden_violations: Tuple[str, ...] = (),
    attribute_hardening_required: Tuple[str, ...] = (),
    unknown_needs_runtime_run: Tuple[str, ...] = (),
    gap_count: int = 0,
    highest_gap_severity: str = "info",
    recommendations: Tuple[str, ...] = (),
    notes: str = "",
    route_shape: str = "R3_grounded_read",
) -> AppCloseoutSummary:
    return AppCloseoutSummary(
        app_name=app_name,
        route_shape=route_shape,
        static_runtime_mode="observed",
        manifest_hash=manifest_hash,
        runtime_certification_status=NOT_CERTIFIED,
        evidence_kind=evidence_kind,
        passed_trace_observed=passed_trace_observed,
        passed_formal_exception_observed=passed_formal_exception_observed,
        missing_contracts=missing_contracts,
        forbidden_violations=forbidden_violations,
        attribute_hardening_required=attribute_hardening_required,
        unknown_needs_runtime_run=unknown_needs_runtime_run,
        gap_count=gap_count,
        highest_gap_severity=highest_gap_severity,
        recommendations=recommendations,
        notes=notes,
    )


def _report(summaries: Tuple[AppCloseoutSummary, ...]) -> PhaseCCloseoutReport:
    trace_ready = sum(
        1
        for s in summaries
        if s.evidence_kind in (EVIDENCE_KIND_R3, EVIDENCE_KIND_BTC)
        and s.passed_trace_observed
    )
    formal_ready = sum(
        1
        for s in summaries
        if s.evidence_kind == "formal_exception_observed"
        and s.passed_formal_exception_observed
    )
    blockers = sum(1 for s in summaries if s.has_blocker)
    return PhaseCCloseoutReport(
        generated_at=GEN_AT,
        app_summaries=summaries,
        total_apps=len(summaries),
        not_certified_count=len(summaries),
        trace_observed_ready_count=trace_ready,
        formal_exception_observed_ready_count=formal_ready,
        blocker_count=blockers,
        top_recommendations=(),
        runtime_certification_status=NOT_CERTIFIED,
        disclaimer=REPORT_DISCLAIMER,
    )


def _prior_record(
    *,
    app_name: str,
    manifest_hash: str,
    trace_observed_n: int,
    trace_observed_success_n: int,
    evidence_rate: float | None = None,
    generated_at_utc: str = "2026-04-24T12:00:00Z",
    verdict: str = VERDICT_HOLD,
) -> CertificationDecisionRecord:
    rate = (
        evidence_rate
        if evidence_rate is not None
        else (
            trace_observed_success_n / trace_observed_n
            if trace_observed_n > 0
            else 0.0
        )
    )
    return make_certification_decision_record(
        generated_at_utc=generated_at_utc,
        app_name=app_name,
        route_shape="R3_grounded_read",
        manifest_hash=manifest_hash,
        evidence_kind=EVIDENCE_KIND_R3,
        closeout_report_id="prior-report",
        closeout_report_hash=_h(f"prior-{app_name}-{generated_at_utc}"),
        trace_observed_n=trace_observed_n,
        trace_observed_success_n=trace_observed_success_n,
        evidence_rate=rate,
        wilson_lower=0.55,
        z_score=1.5,
        uplift=0.0,
        verdict=verdict,
        failure_reasons=(SAMPLE_SIZE_TOO_SMALL,),
        next_review_utc="2026-05-01T12:00:00Z",
    )


def _certify_history(app_name: str) -> Tuple[CertificationDecisionRecord, ...]:
    """29 accumulators (1,1) for same manifest + most-recent (2,1) baseline.

    Mirrors ``_certify_fixture`` in test_cert_decision_evaluator so the
    smoke can drive a VERDICT_CERTIFY end-to-end.
    """
    accumulators = [
        _prior_record(
            app_name=app_name,
            manifest_hash=MANIFEST_A,
            trace_observed_n=1,
            trace_observed_success_n=1,
            generated_at_utc=f"2026-04-{1 + i:02d}T12:00:00Z",
        )
        for i in range(29)
    ]
    most_recent = _prior_record(
        app_name=app_name,
        manifest_hash=MANIFEST_A,
        trace_observed_n=2,
        trace_observed_success_n=1,
        evidence_rate=0.5,
        generated_at_utc="2026-04-30T12:00:00Z",
    )
    return tuple(accumulators) + (most_recent,)


# ===========================================================================
# Test 1: hold-verdict round trip.
# ===========================================================================


def test_smoke_hold_verdict_round_trip(tmp_path: Path) -> None:
    summary = _summary(passed_trace_observed=True)  # small n -> SAMPLE_SIZE_TOO_SMALL
    report = _report((summary,))

    result = run_cert_decision_smoke(report, repo_root=tmp_path)

    assert result.input_app_count == 1
    assert result.decision_count == 1
    assert result.written_count == 1
    assert result.already_exists_count == 0
    assert result.skipped_count == 0
    assert result.read_back_count == 1
    assert result.runtime_certification_status == NOT_CERTIFIED
    assert result.verdicts == (VERDICT_HOLD,)
    assert len(result.decision_ids) == 1
    assert len(result.ledger_paths) == 1
    assert result.ledger_paths[0] == ledger_path_for_app(
        "apps_research", repo_root=tmp_path
    )
    assert result.failure_reasons == ()
    (rec,) = result.read_back_records
    assert rec.runtime_certification_status_before == NOT_CERTIFIED
    assert rec.runtime_certification_status_after == NOT_CERTIFIED
    assert rec.verdict == VERDICT_HOLD


# ===========================================================================
# Test 2: certify verdict — still NOT_CERTIFIED end-to-end.
# ===========================================================================


def test_smoke_certify_verdict_still_not_certified(tmp_path: Path) -> None:
    summary = _summary(passed_trace_observed=True)
    history = _certify_history("apps_research")
    report = _report((summary,))

    result = run_cert_decision_smoke(report, repo_root=tmp_path, history=history)

    assert result.decision_count == 1
    assert result.written_count == 1
    assert result.read_back_count == 1
    assert result.failure_reasons == ()
    (rec,) = result.read_back_records
    # Load-bearing non-promotion invariant: certify != certification.
    assert rec.verdict == VERDICT_CERTIFY
    assert rec.runtime_certification_status_before == NOT_CERTIFIED
    assert rec.runtime_certification_status_after == NOT_CERTIFIED
    assert result.runtime_certification_status == NOT_CERTIFIED


# ===========================================================================
# Test 3: reject-verdict round trip (missing-contracts fixture).
# ===========================================================================


def test_smoke_reject_verdict_round_trip(tmp_path: Path) -> None:
    # Missing R3 contracts -> verdict=reject with non-empty failure_reasons
    # on the stored record itself.
    summary = _summary(
        passed_trace_observed=False,
        missing_contracts=("GroundedReadRequest", "RetrievedContextSlate"),
        gap_count=2,
        highest_gap_severity="critical",
    )
    report = _report((summary,))

    result = run_cert_decision_smoke(report, repo_root=tmp_path)

    assert result.decision_count == 1
    assert result.written_count == 1
    assert result.read_back_count == 1
    # Smoke harness itself succeeded (no diagnostics) — the decision says
    # reject; that is an outcome, not a harness failure.
    assert result.failure_reasons == ()
    (rec,) = result.read_back_records
    assert rec.verdict == VERDICT_REJECT
    assert len(rec.failure_reasons) >= 1  # reject always carries reasons
    assert rec.runtime_certification_status_after == NOT_CERTIFIED


# ===========================================================================
# Test 4: idempotent second run.
# ===========================================================================


def test_smoke_idempotent_second_run(tmp_path: Path) -> None:
    summary = _summary(passed_trace_observed=True)
    report = _report((summary,))

    first = run_cert_decision_smoke(report, repo_root=tmp_path)
    assert first.written_count == 1
    assert first.already_exists_count == 0
    assert first.read_back_count == 1
    assert first.failure_reasons == ()

    second = run_cert_decision_smoke(report, repo_root=tmp_path)
    assert second.written_count == 0
    assert second.already_exists_count == 1
    assert second.skipped_count == 0
    assert second.read_back_count == 1
    assert second.failure_reasons == ()
    # Same decision_id on both runs (deterministic).
    assert first.decision_ids == second.decision_ids


# ===========================================================================
# Test 5: fail-soft skipped write surfaces in report.
# ===========================================================================


def test_smoke_fail_soft_skipped_surfaces_in_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    summary = _summary(passed_trace_observed=True)
    report = _report((summary,))

    def _fake_write(
        record: CertificationDecisionRecord,
        *,
        repo_root,
        fail_soft: bool = True,
    ) -> CertDecisionLedgerWriteResult:
        return CertDecisionLedgerWriteResult(
            app_name=record.app_name,
            ledger_path=ledger_path_for_app(
                record.app_name, repo_root=repo_root
            ),
            decision_id=record.decision_id,
            written=False,
            already_exists=False,
            skipped=True,
            error="sqlite3.OperationalError: injected failure",
            notes="fail-soft smoke injection",
        )

    monkeypatch.setattr(smoke, "write_cert_decision_record", _fake_write)

    result = run_cert_decision_smoke(report, repo_root=tmp_path)

    assert result.written_count == 0
    assert result.already_exists_count == 0
    assert result.skipped_count == 1
    assert result.read_back_count == 0  # nothing was actually written
    assert LEDGER_WRITE_SKIPPED in result.failure_reasons
    # No MISSING_READBACK because the expected-in-readback set excludes skipped writes.
    assert MISSING_READBACK not in result.failure_reasons
    assert "injected failure" in result.notes


# ===========================================================================
# Test 6: missing read-back triggers MISSING_READBACK.
# ===========================================================================


def test_smoke_missing_readback_creates_failure_reason(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    summary = _summary(passed_trace_observed=True)
    report = _report((summary,))

    def _empty_readback(app_name: str, *, repo_root=None):
        return ()

    monkeypatch.setattr(smoke, "read_cert_decision_records", _empty_readback)

    result = run_cert_decision_smoke(report, repo_root=tmp_path)

    assert result.written_count == 1
    assert result.read_back_count == 0
    assert MISSING_READBACK in result.failure_reasons


# ===========================================================================
# Test 7: report writer JSON carries disclaimer + NOT_CERTIFIED.
# ===========================================================================


def test_smoke_report_writer_includes_disclaimer(tmp_path: Path) -> None:
    summary = _summary(passed_trace_observed=True)
    report = _report((summary,))
    smoke_report = run_cert_decision_smoke(report, repo_root=tmp_path)

    out = write_cert_decision_smoke_report(smoke_report, tmp_path / "smoke.json")
    assert out.exists()
    payload = json.loads(out.read_text(encoding="utf-8"))

    assert payload["disclaimer"] == DISCLAIMER
    assert "no runtime certification performed" in payload["disclaimer"]
    assert payload["runtime_certification_status"] == NOT_CERTIFIED
    assert payload["schema_version"] == SCHEMA_VERSION
    assert payload["decision_count"] == 1
    assert isinstance(payload["ledger_paths"], list)
    assert isinstance(payload["ledger_paths"][0], str)  # Path -> str
    assert isinstance(payload["write_results"], list)
    assert payload["write_results"][0]["written"] is True


def test_smoke_report_writer_rejects_non_report_object(tmp_path: Path) -> None:
    with pytest.raises(TypeError, match="CertDecisionSmokeReport"):
        write_cert_decision_smoke_report(
            {"not": "a report"},  # type: ignore[arg-type]
            tmp_path / "bad.json",
        )


def test_smoke_report_writer_creates_parent_dirs(tmp_path: Path) -> None:
    summary = _summary(passed_trace_observed=True)
    smoke_report = run_cert_decision_smoke(
        _report((summary,)), repo_root=tmp_path
    )
    deep = tmp_path / "a" / "b" / "c" / "smoke.json"
    out = write_cert_decision_smoke_report(smoke_report, deep)
    assert out.exists()


# ===========================================================================
# Test 8: dataclass rejects non-NOT_CERTIFIED status.
# ===========================================================================


def _valid_smoke_report_kwargs() -> dict:
    """Minimal valid constructor kwargs for CertDecisionSmokeReport."""
    return dict(
        generated_at_utc=GEN_AT,
        input_app_count=0,
        decision_count=0,
        written_count=0,
        already_exists_count=0,
        skipped_count=0,
        read_back_count=0,
        runtime_certification_status=NOT_CERTIFIED,
        decision_ids=(),
        ledger_paths=(),
        verdicts=(),
        write_results=(),
        read_back_records=(),
        failure_reasons=(),
    )


def test_report_dataclass_rejects_runtime_certified() -> None:
    kwargs = _valid_smoke_report_kwargs()
    kwargs["runtime_certification_status"] = "RUNTIME_CERTIFIED"
    with pytest.raises(ValueError, match="NOT_CERTIFIED"):
        CertDecisionSmokeReport(**kwargs)


def test_report_dataclass_rejects_formal_exception_verified() -> None:
    kwargs = _valid_smoke_report_kwargs()
    kwargs["runtime_certification_status"] = "FORMAL_EXCEPTION_VERIFIED"
    with pytest.raises(ValueError, match="NOT_CERTIFIED"):
        CertDecisionSmokeReport(**kwargs)


def test_report_dataclass_rejects_bad_schema_version() -> None:
    kwargs = _valid_smoke_report_kwargs()
    kwargs["schema_version"] = "v2"
    with pytest.raises(ValueError, match="schema_version"):
        CertDecisionSmokeReport(**kwargs)


def test_report_dataclass_rejects_disclaimer_missing_phrase() -> None:
    kwargs = _valid_smoke_report_kwargs()
    kwargs["disclaimer"] = "this just says things"
    with pytest.raises(ValueError, match="disclaimer"):
        CertDecisionSmokeReport(**kwargs)


# ===========================================================================
# Test count-balance invariants.
# ===========================================================================


def test_report_dataclass_rejects_mismatched_counts() -> None:
    kwargs = _valid_smoke_report_kwargs()
    kwargs["decision_count"] = 2
    kwargs["written_count"] = 1
    kwargs["already_exists_count"] = 0
    kwargs["skipped_count"] = 0  # 1 != 2
    # Also need to bump parallel tuples to match decision_count for the
    # length-check step; but we WANT the balance check to fire, not the
    # length check. So give correct-length tuples.
    kwargs["decision_ids"] = ("a" * 64, "b" * 64)
    kwargs["verdicts"] = (VERDICT_HOLD, VERDICT_HOLD)
    kwargs["ledger_paths"] = (Path("p1"), Path("p2"))
    # write_results must reflect one written result for the flag-count check.
    kwargs["write_results"] = (
        CertDecisionLedgerWriteResult(
            app_name="apps_research",
            ledger_path=Path("p1"),
            decision_id="a" * 64,
            written=True,
        ),
        CertDecisionLedgerWriteResult(
            app_name="apps_research",
            ledger_path=Path("p2"),
            decision_id="b" * 64,
            written=True,
        ),
    )
    kwargs["written_count"] = 1  # lie
    with pytest.raises(ValueError, match="written_count|balance|disagrees"):
        CertDecisionSmokeReport(**kwargs)


def test_report_dataclass_rejects_decision_ids_length_mismatch() -> None:
    kwargs = _valid_smoke_report_kwargs()
    kwargs["decision_count"] = 1
    # Provide decision_ids of wrong length, keep everything else at length 0.
    kwargs["decision_ids"] = ("a" * 64, "b" * 64)
    with pytest.raises(ValueError, match="decision_ids"):
        CertDecisionSmokeReport(**kwargs)


def test_report_dataclass_rejects_negative_count() -> None:
    kwargs = _valid_smoke_report_kwargs()
    kwargs["decision_count"] = -1
    with pytest.raises(ValueError, match=">= 0"):
        CertDecisionSmokeReport(**kwargs)


def test_report_dataclass_rejects_unknown_failure_reason() -> None:
    kwargs = _valid_smoke_report_kwargs()
    kwargs["failure_reasons"] = ("SOMETHING_ELSE",)
    with pytest.raises(ValueError, match="unknown reason"):
        CertDecisionSmokeReport(**kwargs)


# ===========================================================================
# Test 9: smoke does not write to real repo artifacts/ledgers.
# ===========================================================================


def test_smoke_does_not_write_to_real_artifacts_ledgers(tmp_path: Path) -> None:
    summary = _summary(passed_trace_observed=True, app_name="apps_smoke_probe")
    # C.8 summary app_name validator is lenient (any apps_* prefix); if
    # apps_smoke_probe is rejected, fall back to apps_research.
    try:
        report = _report((summary,))
    except (ValueError, TypeError):
        summary = _summary(passed_trace_observed=True)
        report = _report((summary,))

    real_repo_root = Path(__file__).resolve().parents[5]
    real_ledger = (
        real_repo_root
        / "artifacts"
        / "ledgers"
        / f"cert_decision_{summary.app_name}.sqlite"
    )
    existed_before = real_ledger.exists()

    run_cert_decision_smoke(report, repo_root=tmp_path)

    # The tmp_path ledger was written.
    assert (
        tmp_path
        / "artifacts"
        / "ledgers"
        / f"cert_decision_{summary.app_name}.sqlite"
    ).exists()
    # The real-repo ledger file is unchanged: either still missing, or
    # still present if it was present before. No *new* real-repo ledger
    # file was created by this test.
    assert real_ledger.exists() is existed_before


# ===========================================================================
# Test 10: no forbidden imports.
# ===========================================================================


def test_smoke_no_scanner_ci_emitter_imports() -> None:
    # Inspect the smoke module's source directly — robust against import-
    # order side effects from other tests that may have pre-loaded
    # unrelated modules into sys.modules.
    src = Path(smoke.__file__).read_text(encoding="utf-8")
    forbidden_patterns = [
        r"agentic_core\.L\d_",
        r"ops_scripts\.ci",
        r"tools\.spine\.scanner",
    ]
    for pattern in forbidden_patterns:
        assert re.search(pattern, src) is None, (
            f"smoke module source contains forbidden pattern {pattern!r}"
        )


# ===========================================================================
# Test 11: multi-app single call.
# ===========================================================================


def test_smoke_multiple_apps_one_call(tmp_path: Path) -> None:
    # Three summaries -> three distinct ledger files, three read-backs.
    s1 = _summary(
        app_name="apps_research",
        manifest_hash=MANIFEST_A,
        passed_trace_observed=True,
    )
    s2 = _summary(
        app_name="apps_knowledge_capture",
        manifest_hash=MANIFEST_B,
        passed_trace_observed=False,
        missing_contracts=("GroundedReadRequest",),
        gap_count=1,
        highest_gap_severity="critical",
    )
    s3 = _summary(
        app_name="apps_evidence",
        manifest_hash=MANIFEST_C,
        passed_trace_observed=True,
    )
    report = _report((s1, s2, s3))

    result = run_cert_decision_smoke(report, repo_root=tmp_path)

    assert result.input_app_count == 3
    assert result.decision_count == 3
    assert result.written_count == 3
    assert result.read_back_count == 3
    # Three distinct ledger files.
    assert len({str(p) for p in result.ledger_paths}) == 3
    for p in result.ledger_paths:
        assert p.exists()
    assert DECISION_COUNT_DOES_NOT_MATCH_INPUT not in result.failure_reasons


# ===========================================================================
# Test 12: order preservation.
# ===========================================================================


def test_smoke_preserves_input_order(tmp_path: Path) -> None:
    summaries = (
        _summary(
            app_name="apps_research",
            manifest_hash=MANIFEST_A,
            passed_trace_observed=True,
        ),
        _summary(
            app_name="apps_knowledge_capture",
            manifest_hash=MANIFEST_B,
            passed_trace_observed=False,
            missing_contracts=("GroundedReadRequest",),
            gap_count=1,
            highest_gap_severity="critical",
        ),
        _summary(
            app_name="apps_evidence",
            manifest_hash=MANIFEST_C,
            passed_trace_observed=True,
        ),
    )
    report = _report(summaries)

    result = run_cert_decision_smoke(report, repo_root=tmp_path)

    assert len(result.decision_ids) == 3
    assert len(result.verdicts) == 3
    # First app is the one in the first summary, etc.
    assert result.write_results[0].app_name == "apps_research"
    assert result.write_results[1].app_name == "apps_knowledge_capture"
    assert result.write_results[2].app_name == "apps_evidence"


# ===========================================================================
# Test 13: repo_root is required.
# ===========================================================================


def test_repo_root_is_required_positionally(tmp_path: Path) -> None:
    summary = _summary(passed_trace_observed=True)
    report = _report((summary,))
    # Must pass by keyword — signature forbids positional.
    with pytest.raises(TypeError):
        run_cert_decision_smoke(report)  # type: ignore[call-arg]


def test_repo_root_rejects_none() -> None:
    summary = _summary(passed_trace_observed=True)
    report = _report((summary,))
    with pytest.raises(ValueError, match="repo_root"):
        run_cert_decision_smoke(report, repo_root=None)  # type: ignore[arg-type]


def test_run_rejects_non_closeout_report(tmp_path: Path) -> None:
    with pytest.raises(TypeError, match="PhaseCCloseoutReport"):
        run_cert_decision_smoke(
            {"not": "a report"},  # type: ignore[arg-type]
            repo_root=tmp_path,
        )


# ===========================================================================
# Test 14: to_dict / to_json are JSON-safe.
# ===========================================================================


def test_to_dict_and_to_json_are_json_safe(tmp_path: Path) -> None:
    summary = _summary(passed_trace_observed=True)
    report = _report((summary,))
    smoke_report = run_cert_decision_smoke(report, repo_root=tmp_path)

    # to_dict() produces only JSON-native types (no Path, no dataclass).
    d = smoke_report.to_dict()

    def _assert_json_safe(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                assert isinstance(k, str), f"non-string key at {path}"
                _assert_json_safe(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                _assert_json_safe(v, f"{path}[{i}]")
        else:
            assert isinstance(
                obj, (str, int, float, bool, type(None))
            ), f"non-JSON-safe value at {path}: {type(obj).__name__}"

    _assert_json_safe(d)
    # Round-trip.
    parsed = json.loads(smoke_report.to_json())
    assert parsed["schema_version"] == SCHEMA_VERSION
    assert parsed["disclaimer"] == DISCLAIMER
    assert parsed["runtime_certification_status"] == NOT_CERTIFIED


# ===========================================================================
# Test: failure-reason ontology is closed.
# ===========================================================================


def test_smoke_failure_reasons_ontology_is_closed() -> None:
    assert SMOKE_FAILURE_REASONS == frozenset(
        {
            "WRITE_COUNT_MISMATCH",
            "LEDGER_WRITE_SKIPPED",
            "MISSING_READBACK",
            "STATUS_NOT_NOT_CERTIFIED",
            "DECISION_COUNT_DOES_NOT_MATCH_INPUT",
            "READBACK_DECISION_ID_MISMATCH",
        }
    )


# ===========================================================================
# Test: ledger_paths contain resolved tmp_path — not real repo.
# ===========================================================================


def test_smoke_ledger_paths_under_tmp_path(tmp_path: Path) -> None:
    summary = _summary(passed_trace_observed=True)
    report = _report((summary,))
    result = run_cert_decision_smoke(report, repo_root=tmp_path)

    resolved_tmp = tmp_path.resolve()
    for p in result.ledger_paths:
        # Every ledger path lives under resolved tmp_path.
        assert str(p).startswith(str(resolved_tmp)), (
            f"{p} is not under {resolved_tmp}"
        )
