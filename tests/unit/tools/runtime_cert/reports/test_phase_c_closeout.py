"""Unit tests for Phase C closeout — non-promoting readiness aggregator.

All tests use synthetic ``NormalizedTraceRow`` fixtures + the real
contract factories. No live SQLite, no runtime ADG query, no real
manifest filesystem reads.

Test plan reference: task spec §7 (11 required tests).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from agentic_core.L6_system_learning.app_route_contracts import (
    BUILD_TIME_COMPILER_CONTRACTS,
    R3_GROUNDED_READ_CONTRACTS,
    RouteShape,
    build_build_time_compiler_contract,
    build_formal_exception_contract,
    build_r3_grounded_read_contract,
)
from tools.runtime_cert.reports.phase_c_closeout import (
    AppCloseoutSummary,
    EVIDENCE_KIND_BTC,
    EVIDENCE_KIND_FORMAL_EXCEPTION,
    EVIDENCE_KIND_R3,
    PhaseCCloseoutReport,
    REPORT_DISCLAIMER,
    build_phase_c_closeout_report,
    write_phase_c_closeout_markdown,
)
from tools.runtime_cert.runtime_adg_query_adapter import NOT_CERTIFIED
from tools.runtime_cert.trace_row_normalizer import (
    ATTRIBUTE_HARDENING_REQUIRED,
    EXISTS_MATCHES_MATRIX,
    FORBIDDEN_SPAN_VIOLATION,
    NormalizedTraceRow,
    UNKNOWN_NEEDS_RUNTIME_RUN,
)

# ---------------------------------------------------------------------------
# Constants / fixture helpers
# ---------------------------------------------------------------------------

_HASH = "a" * 64


def _r3_contract(app_name: str = "apps_research") -> Any:
    return build_r3_grounded_read_contract(
        app_name=app_name,
        manifest_path=f"{app_name}/spine_manifest.yaml",
        manifest_hash=_HASH,
    )


def _btc_contract(app_name: str = "apps_qna") -> Any:
    return build_build_time_compiler_contract(
        app_name=app_name,
        manifest_path=f"{app_name}/spine_manifest.yaml",
        manifest_hash=_HASH,
    )


def _formal_contract(
    app_name: str = "apps_eval",
    compensating_controls: tuple[str, ...] = ("CC-EVAL-01", "CC-EVAL-02"),
) -> Any:
    return build_formal_exception_contract(
        app_name=app_name,
        route_shape=RouteShape.evaluator_only,
        manifest_path=f"{app_name}/spine_manifest.yaml",
        manifest_hash=_HASH,
        reason_code="evaluator_only",
        compensating_controls=compensating_controls,
    )


def _row(
    *,
    app_name: str,
    contract_name: str | None,
    phase_c_status: str,
    span_id: str = "s1",
    span_name: str = "test.span",
    route_shape: str = "R3_grounded_read",
    mapping_notes: str = "",
    parent_span_id: str | None = None,
    trace_id: str = "trace-test",
    normalized_cert_alias: str | None = None,
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
        source_path=None,
        attributes={},
        evidence_source="runtime_adg.snapshot.test",
    )


def _all_r3_clean_rows(app_name: str = "apps_research") -> list[NormalizedTraceRow]:
    """8 clean rows — one per required R3 contract."""
    return [
        _row(
            app_name=app_name,
            contract_name=c,
            phase_c_status=EXISTS_MATCHES_MATRIX,
            span_id=f"s{i}",
            span_name=f"r3.span.{c}",
        )
        for i, c in enumerate(R3_GROUNDED_READ_CONTRACTS)
    ]


def _all_btc_clean_rows(app_name: str = "apps_qna") -> list[NormalizedTraceRow]:
    return [
        _row(
            app_name=app_name,
            contract_name=c,
            phase_c_status=EXISTS_MATCHES_MATRIX,
            span_id=f"btc{i}",
            span_name=f"btc.span.{c}",
            route_shape="build_time_compiler",
        )
        for i, c in enumerate(BUILD_TIME_COMPILER_CONTRACTS)
    ]


# ---------------------------------------------------------------------------
# T1 — R3 app summary uses extract_r3_evidence + gap report
# ---------------------------------------------------------------------------


def test_r3_app_summary_uses_r3_evidence_and_gap_report():
    """T1: R3 app produces r3-kind summary with evidence + gap-report fields populated."""
    contracts = [_r3_contract()]
    rows = {"apps_research": _all_r3_clean_rows()}
    report = build_phase_c_closeout_report(contracts, rows)

    assert report.runtime_certification_status == NOT_CERTIFIED
    assert report.total_apps == 1
    (s,) = report.app_summaries
    assert s.app_name == "apps_research"
    assert s.evidence_kind == EVIDENCE_KIND_R3
    assert s.runtime_certification_status == NOT_CERTIFIED
    # With 8 clean matrix rows, evidence says all observed; gap report
    # has no gaps on top.
    assert set(s.missing_contracts) == set()
    assert s.gap_count == 0
    assert s.passed_trace_observed is True
    assert s.passed_formal_exception_observed is False


def test_r3_app_summary_honest_when_rows_absent():
    """T1b: R3 app with no rows → all 8 required missing; NOT_CERTIFIED; blocker."""
    contracts = [_r3_contract()]
    report = build_phase_c_closeout_report(contracts, {})
    (s,) = report.app_summaries
    assert s.evidence_kind == EVIDENCE_KIND_R3
    assert set(s.missing_contracts) == set(R3_GROUNDED_READ_CONTRACTS)
    assert s.has_blocker is True
    assert s.passed_trace_observed is False
    assert s.runtime_certification_status == NOT_CERTIFIED
    assert report.blocker_count == 1
    assert report.trace_observed_ready_count == 0


# ---------------------------------------------------------------------------
# T2 — BTC app summary uses extract_btc_evidence + gap report
# ---------------------------------------------------------------------------


def test_btc_app_summary_uses_btc_evidence_and_gap_report():
    """T2: BTC app produces btc-kind summary with evidence + gap-report fields."""
    contracts = [_btc_contract()]
    rows = {"apps_qna": _all_btc_clean_rows()}
    report = build_phase_c_closeout_report(contracts, rows)
    (s,) = report.app_summaries
    assert s.app_name == "apps_qna"
    assert s.evidence_kind == EVIDENCE_KIND_BTC
    assert s.runtime_certification_status == NOT_CERTIFIED
    assert set(s.missing_contracts) == set()


# ---------------------------------------------------------------------------
# T3 — formal exception app uses extract_formal_exception_evidence
# ---------------------------------------------------------------------------


def test_formal_exception_app_summary_uses_formal_extractor():
    """T3: formal-exception app produces formal-kind summary, gap report NOT run."""
    contracts = [_formal_contract()]
    # No rows → CC-EVAL-01 passes (no circularity descendants to find) and
    # CC-EVAL-02 passes (no R3 leak rows). passed_formal_exception_observed=True.
    report = build_phase_c_closeout_report(contracts, {})
    (s,) = report.app_summaries
    assert s.app_name == "apps_eval"
    assert s.evidence_kind == EVIDENCE_KIND_FORMAL_EXCEPTION
    assert s.runtime_certification_status == NOT_CERTIFIED
    # Gap report is explicitly skipped for formal-exception apps.
    assert s.gap_count == 0
    assert (
        "attribute-hardening gap report not run" in s.notes
        or "formal exception class with no required" in s.notes
    )
    # passed_trace_observed is always False for formal-exception apps
    # (because no R3/BTC trace evaluation runs).
    assert s.passed_trace_observed is False


def test_formal_exception_app_failed_controls_are_blockers():
    """T3b: formal-exception app with R3 leak row → failed CC-EVAL-02 → blocker."""
    contract = _formal_contract(
        compensating_controls=("CC-EVAL-01", "CC-EVAL-02"),
    )
    # A SealedArtifact row on apps_eval with a route_shape NOT in the
    # apps_eval allowed-surface set is an R3 leak → CC-EVAL-02 fails.
    leak_row = _row(
        app_name="apps_eval",
        contract_name="SealedArtifact",
        phase_c_status=EXISTS_MATCHES_MATRIX,
        span_name="leak.surface",
        route_shape="R3_grounded_read",  # NOT an apps_eval allowed surface
    )
    report = build_phase_c_closeout_report(
        [contract], {"apps_eval": [leak_row]},
    )
    (s,) = report.app_summaries
    assert s.evidence_kind == EVIDENCE_KIND_FORMAL_EXCEPTION
    assert "CC-EVAL-02" in s.forbidden_violations
    assert s.passed_formal_exception_observed is False
    assert s.has_blocker is True
    assert report.blocker_count == 1


# ---------------------------------------------------------------------------
# T4 — missing rows → honest blockers
# ---------------------------------------------------------------------------


def test_missing_rows_produce_honest_blockers():
    """T4: absent row batch for an app → missing contracts reported; blocker=True."""
    contracts = [_r3_contract("apps_research"), _btc_contract("apps_qna")]
    report = build_phase_c_closeout_report(contracts, {})

    for s in report.app_summaries:
        assert s.runtime_certification_status == NOT_CERTIFIED
        assert s.has_blocker is True
    assert report.blocker_count == 2
    assert report.trace_observed_ready_count == 0


# ---------------------------------------------------------------------------
# T5 — zero-gap R3 app remains NOT_CERTIFIED
# ---------------------------------------------------------------------------


def test_zero_gap_r3_app_still_not_certified():
    """T5: clean R3 app (8 EXISTS_MATCHES_MATRIX rows) → NOT_CERTIFIED everywhere."""
    contracts = [_r3_contract()]
    rows = {"apps_research": _all_r3_clean_rows()}
    report = build_phase_c_closeout_report(contracts, rows)
    (s,) = report.app_summaries
    assert s.runtime_certification_status == NOT_CERTIFIED
    assert report.runtime_certification_status == NOT_CERTIFIED
    assert report.not_certified_count == 1
    # passed_trace_observed=True is allowed — it's a readiness flag, NOT a
    # certification promotion.
    assert s.passed_trace_observed is True


# ---------------------------------------------------------------------------
# T6 — app summaries sorted deterministically
# ---------------------------------------------------------------------------


def test_app_summaries_sorted_by_name():
    """T6: summaries are sorted by app_name regardless of input order."""
    # Input: apps_qna, apps_eval, apps_research
    contracts = [
        _btc_contract("apps_qna"),
        _formal_contract("apps_eval"),
        _r3_contract("apps_research"),
    ]
    report = build_phase_c_closeout_report(contracts, {})
    names = [s.app_name for s in report.app_summaries]
    assert names == sorted(names)
    assert names == ["apps_eval", "apps_qna", "apps_research"]


# ---------------------------------------------------------------------------
# T7 — top recommendations deduped deterministically
# ---------------------------------------------------------------------------


def test_top_recommendations_deduped_deterministically():
    """T7: duplicate recommendations across apps collapse in the top list."""
    # Two R3 apps, both missing the same ExitReviewPacket → same
    # "Add or bind runtime evidence for 'ExitReviewPacket'..." recommendation.
    rows_a = [
        _row(
            app_name="apps_a_research",
            contract_name=c,
            phase_c_status=EXISTS_MATCHES_MATRIX,
            span_id=f"a{i}",
        )
        for i, c in enumerate(R3_GROUNDED_READ_CONTRACTS)
        if c != "ExitReviewPacket"
    ]
    rows_b = [
        _row(
            app_name="apps_b_research",
            contract_name=c,
            phase_c_status=EXISTS_MATCHES_MATRIX,
            span_id=f"b{i}",
        )
        for i, c in enumerate(R3_GROUNDED_READ_CONTRACTS)
        if c != "ExitReviewPacket"
    ]
    contracts = [
        _r3_contract("apps_a_research"),
        _r3_contract("apps_b_research"),
    ]
    rows_by_app = {
        "apps_a_research": rows_a,
        "apps_b_research": rows_b,
    }
    r1 = build_phase_c_closeout_report(contracts, rows_by_app)
    r2 = build_phase_c_closeout_report(contracts, rows_by_app)
    assert r1.top_recommendations == r2.top_recommendations
    # No duplicates
    assert len(r1.top_recommendations) == len(set(r1.top_recommendations))
    # The ExitReviewPacket recommendation appears once
    matching = [
        r for r in r1.top_recommendations if "ExitReviewPacket" in r
    ]
    assert len(matching) == 1


# ---------------------------------------------------------------------------
# T8 — markdown includes disclaimer + NOT_CERTIFIED on every row
# ---------------------------------------------------------------------------


def test_markdown_includes_disclaimer_and_not_certified(tmp_path):
    """T8: markdown writer emits disclaimer + NOT_CERTIFIED per row + next-phase note."""
    contracts = [_r3_contract(), _btc_contract(), _formal_contract()]
    rows = {"apps_research": _all_r3_clean_rows()}
    report = build_phase_c_closeout_report(contracts, rows)

    out_path = tmp_path / "closeout.md"
    written = write_phase_c_closeout_markdown(report, out_path)
    text = written.read_text(encoding="utf-8")

    assert REPORT_DISCLAIMER in text
    assert "No runtime certification performed" in text
    assert "Phase D planning is required" in text
    # Every app row has NOT_CERTIFIED rendered as a code span
    for app in ("apps_research", "apps_qna", "apps_eval"):
        assert app in text
    # Every row shows `NOT_CERTIFIED`; count at least the number of apps
    assert text.count("NOT_CERTIFIED") >= 1 + len(report.app_summaries)


def test_markdown_writer_creates_parent_directories(tmp_path):
    """T8b: writer creates parent directories if absent."""
    contracts = [_r3_contract()]
    report = build_phase_c_closeout_report(contracts, {})
    nested = tmp_path / "deep" / "nested" / "closeout.md"
    written = write_phase_c_closeout_markdown(report, nested)
    assert written.exists()


def test_markdown_writer_refuses_non_not_certified_report(tmp_path):
    """T8c: writer refuses to emit a non-NOT_CERTIFIED report."""
    contracts = [_r3_contract()]
    report = build_phase_c_closeout_report(contracts, {})
    # Bypass frozen-dataclass to force a bad status.
    object.__setattr__(report, "runtime_certification_status", "RUNTIME_CERTIFIED")
    with pytest.raises(ValueError, match="runtime_certification_status"):
        write_phase_c_closeout_markdown(report, tmp_path / "x.md")


def test_markdown_no_blockers_section_when_clean(tmp_path):
    """T8d: clean report still emits a Blockers section with an empty-state marker."""
    contracts = [_r3_contract()]
    rows = {"apps_research": _all_r3_clean_rows()}
    report = build_phase_c_closeout_report(contracts, rows)
    out_path = tmp_path / "clean.md"
    written = write_phase_c_closeout_markdown(report, out_path)
    text = written.read_text(encoding="utf-8")
    assert "## Blockers" in text
    assert "_No apps currently block" in text


# ---------------------------------------------------------------------------
# T9 — runtime_certification_status invariant
# ---------------------------------------------------------------------------


def test_report_rejects_non_not_certified_status():
    """T9: PhaseCCloseoutReport constructor rejects any other status."""
    with pytest.raises(ValueError, match="NOT_CERTIFIED"):
        PhaseCCloseoutReport(
            generated_at="2026-04-30T00:00:00+00:00",
            app_summaries=(),
            total_apps=0,
            not_certified_count=0,
            trace_observed_ready_count=0,
            formal_exception_observed_ready_count=0,
            blocker_count=0,
            top_recommendations=(),
            runtime_certification_status="RUNTIME_CERTIFIED",
            disclaimer=REPORT_DISCLAIMER,
        )


def test_summary_rejects_non_not_certified_status():
    """T9b: AppCloseoutSummary constructor rejects any other status."""
    with pytest.raises(ValueError, match="NOT_CERTIFIED"):
        AppCloseoutSummary(
            app_name="apps_x",
            route_shape="R3_grounded_read",
            static_runtime_mode="",
            manifest_hash=_HASH,
            runtime_certification_status="FORMAL_EXCEPTION_VERIFIED",
            evidence_kind=EVIDENCE_KIND_R3,
            passed_trace_observed=True,
            passed_formal_exception_observed=False,
            missing_contracts=(),
            forbidden_violations=(),
            attribute_hardening_required=(),
            unknown_needs_runtime_run=(),
            gap_count=0,
            highest_gap_severity="INFO",
            recommendations=(),
            notes="",
        )


def test_summary_rejects_bad_evidence_kind():
    """T9c: AppCloseoutSummary rejects unknown evidence_kind."""
    with pytest.raises(ValueError, match="evidence_kind"):
        AppCloseoutSummary(
            app_name="apps_x",
            route_shape="R3_grounded_read",
            static_runtime_mode="",
            manifest_hash=_HASH,
            runtime_certification_status=NOT_CERTIFIED,
            evidence_kind="nonsense",
            passed_trace_observed=False,
            passed_formal_exception_observed=False,
            missing_contracts=(),
            forbidden_violations=(),
            attribute_hardening_required=(),
            unknown_needs_runtime_run=(),
            gap_count=0,
            highest_gap_severity="INFO",
            recommendations=(),
            notes="",
        )


def test_report_rejects_count_mismatch():
    """PhaseCCloseoutReport rejects mismatched not_certified_count."""
    with pytest.raises(ValueError, match="not_certified_count"):
        PhaseCCloseoutReport(
            generated_at="2026-04-30T00:00:00+00:00",
            app_summaries=(),
            total_apps=0,
            not_certified_count=5,  # mismatch
            trace_observed_ready_count=0,
            formal_exception_observed_ready_count=0,
            blocker_count=0,
            top_recommendations=(),
            runtime_certification_status=NOT_CERTIFIED,
            disclaimer=REPORT_DISCLAIMER,
        )


# ---------------------------------------------------------------------------
# T10 — no filesystem scan required for core builder
# ---------------------------------------------------------------------------


def test_core_builder_performs_no_filesystem_scan(monkeypatch):
    """T10: builder does NOT invoke any filesystem reads (pure in-memory)."""
    from pathlib import Path as RealPath

    original_glob = RealPath.glob
    original_exists = RealPath.exists
    original_read_text = RealPath.read_text

    glob_calls: list[Any] = []
    exists_calls: list[Any] = []
    read_text_calls: list[Any] = []

    def traced_glob(self, pattern):
        glob_calls.append((self, pattern))
        return original_glob(self, pattern)

    def traced_exists(self):
        exists_calls.append(self)
        return original_exists(self)

    def traced_read_text(self, *args, **kwargs):
        read_text_calls.append(self)
        return original_read_text(self, *args, **kwargs)

    monkeypatch.setattr(RealPath, "glob", traced_glob, raising=True)
    monkeypatch.setattr(RealPath, "exists", traced_exists, raising=True)
    monkeypatch.setattr(RealPath, "read_text", traced_read_text, raising=True)

    contracts = [_r3_contract(), _btc_contract(), _formal_contract()]
    rows = {"apps_research": _all_r3_clean_rows()}
    build_phase_c_closeout_report(contracts, rows)

    # The core builder MUST NOT touch the filesystem. (Manifest hashes
    # live on the contract; evidence extractors accept the contract hash
    # as-is when non-empty.)
    assert glob_calls == []
    assert exists_calls == []
    assert read_text_calls == []


# ---------------------------------------------------------------------------
# T11 — rows from other apps do not contaminate summaries
# ---------------------------------------------------------------------------


def test_rows_from_other_apps_do_not_contaminate():
    """T11: rows_by_app lookups are per-app; unrelated rows are never mixed in."""
    contracts = [_r3_contract("apps_research")]
    # Provide rows only under a different key — should be ignored
    rows = {
        "apps_other": [
            _row(
                app_name="apps_other",
                contract_name="SealedArtifact",
                phase_c_status=FORBIDDEN_SPAN_VIOLATION,
                span_name="apps_other.seal",
            ),
        ],
    }
    report = build_phase_c_closeout_report(contracts, rows)
    (s,) = report.app_summaries
    assert s.app_name == "apps_research"
    assert s.forbidden_violations == ()
    # Missing everything because apps_research rows were never supplied
    assert set(s.missing_contracts) == set(R3_GROUNDED_READ_CONTRACTS)


def test_same_key_but_foreign_rows_filtered_by_extractors():
    """Rows keyed for the target app but with app_name=other still don't contaminate.

    The R3 extractor itself filters by contract.app_name, so even
    incorrectly-keyed rows don't introduce forbidden violations for the
    target app.
    """
    contracts = [_r3_contract("apps_research")]
    rows = {
        "apps_research": [
            # Row keyed under apps_research but with app_name=apps_other
            _row(
                app_name="apps_other",
                contract_name="CommitRequest",
                phase_c_status=FORBIDDEN_SPAN_VIOLATION,
                span_name="apps_other.commit",
            ),
        ],
    }
    report = build_phase_c_closeout_report(contracts, rows)
    (s,) = report.app_summaries
    # CommitRequest row was from apps_other → filtered out by the R3
    # extractor's app scope; no forbidden violation reported for
    # apps_research.
    assert s.forbidden_violations == ()


# ---------------------------------------------------------------------------
# Additional — generated_at + ready-count aggregation + to_dict
# ---------------------------------------------------------------------------


def test_generated_at_override_is_preserved():
    """Explicit generated_at is preserved verbatim."""
    contracts = [_r3_contract()]
    report = build_phase_c_closeout_report(
        contracts, {}, generated_at="2026-04-30T21:00:00+00:00",
    )
    assert report.generated_at == "2026-04-30T21:00:00+00:00"


def test_ready_counts_aggregate_across_apps():
    """Mixed R3/BTC/formal apps populate all three ready counts correctly."""
    contracts = [
        _r3_contract("apps_research"),
        _btc_contract("apps_qna"),
        _formal_contract("apps_eval", ("CC-EVAL-01", "CC-EVAL-02")),
    ]
    rows = {
        "apps_research": _all_r3_clean_rows("apps_research"),
        "apps_qna": _all_btc_clean_rows("apps_qna"),
        # apps_eval: no rows → CC-EVAL-01/02 both pass on empty input
    }
    report = build_phase_c_closeout_report(contracts, rows)

    assert report.total_apps == 3
    assert report.not_certified_count == 3
    assert report.trace_observed_ready_count == 2  # R3 + BTC clean
    assert report.formal_exception_observed_ready_count == 1  # apps_eval
    # apps_eval still technically has no blocker if all listed controls pass.
    # apps_research + apps_qna are clean → no blockers.
    assert report.blocker_count == 0


def test_report_to_dict_json_serialisable():
    """Report + summary to_dict() are JSON-serialisable."""
    import json

    contracts = [_r3_contract(), _formal_contract()]
    rows = {"apps_research": _all_r3_clean_rows()}
    report = build_phase_c_closeout_report(contracts, rows)
    d = report.to_dict()
    text = json.dumps(d)
    assert "NOT_CERTIFIED" in text
    assert d["disclaimer"] == REPORT_DISCLAIMER
    for s_dict in d["app_summaries"]:
        assert s_dict["runtime_certification_status"] == NOT_CERTIFIED


def test_forbidden_rows_contract_names_captured_in_summary():
    """R3 app with a CommitRequest row captures 'CommitRequest' in forbidden_violations."""
    contract = _r3_contract("apps_research")
    rows = {
        "apps_research": _all_r3_clean_rows()
        + [
            _row(
                app_name="apps_research",
                contract_name="CommitRequest",
                phase_c_status=FORBIDDEN_SPAN_VIOLATION,
                span_name="CommitRequest",
                span_id="s_commit",
            ),
        ],
    }
    report = build_phase_c_closeout_report([contract], rows)
    (s,) = report.app_summaries
    assert "CommitRequest" in s.forbidden_violations
    assert s.passed_trace_observed is False
    assert s.has_blocker is True
    assert report.blocker_count == 1


def test_hardening_contracts_flow_through_summary():
    """ATTRIBUTE_HARDENING_REQUIRED row on R3 app → attribute_hardening_required filled."""
    # Craft 7 clean + 1 hardening row for SealedArtifact
    rows = [
        _row(
            app_name="apps_research",
            contract_name=c,
            phase_c_status=EXISTS_MATCHES_MATRIX,
            span_id=f"s{i}",
        )
        for i, c in enumerate(R3_GROUNDED_READ_CONTRACTS)
        if c != "SealedArtifact"
    ]
    rows.append(
        _row(
            app_name="apps_research",
            contract_name="SealedArtifact",
            phase_c_status=ATTRIBUTE_HARDENING_REQUIRED,
            span_name="l2.step.seal",
            mapping_notes="Missing required attributes: ['run_id'].",
            span_id="s_seal",
        ),
    )
    report = build_phase_c_closeout_report(
        [_r3_contract("apps_research")],
        {"apps_research": rows},
    )
    (s,) = report.app_summaries
    assert "SealedArtifact" in s.attribute_hardening_required
    assert s.passed_trace_observed is False
    assert s.has_blocker is True


def test_unknown_runtime_run_flows_through_summary():
    """UNKNOWN_NEEDS_RUNTIME_RUN row → unknown_needs_runtime_run filled."""
    rows = [
        _row(
            app_name="apps_research",
            contract_name=c,
            phase_c_status=EXISTS_MATCHES_MATRIX,
            span_id=f"s{i}",
        )
        for i, c in enumerate(R3_GROUNDED_READ_CONTRACTS)
        if c != "FinalEvidenceContract"
    ]
    rows.append(
        _row(
            app_name="apps_research",
            contract_name="FinalEvidenceContract",
            phase_c_status=UNKNOWN_NEEDS_RUNTIME_RUN,
            span_name="final.evidence",
            span_id="s_final",
        ),
    )
    report = build_phase_c_closeout_report(
        [_r3_contract("apps_research")],
        {"apps_research": rows},
    )
    (s,) = report.app_summaries
    assert "FinalEvidenceContract" in s.unknown_needs_runtime_run
    assert s.has_blocker is True


def test_empty_contracts_produces_empty_report():
    """Zero contracts → empty report, still NOT_CERTIFIED."""
    report = build_phase_c_closeout_report([], {})
    assert report.total_apps == 0
    assert report.not_certified_count == 0
    assert report.blocker_count == 0
    assert report.app_summaries == ()
    assert report.runtime_certification_status == NOT_CERTIFIED
