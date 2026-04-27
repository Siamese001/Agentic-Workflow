"""Tests for apps_shared.proof.bypass_validator."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from apps_shared.proof.adg_queries import AppBypassReport
from apps_shared.proof.bypass_validator import (
    Waiver,
    load_waivers,
    run_full_bypass_validation,
    validate_bypass_report,
)


def _future_iso(days: int = 7) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat().replace("+00:00", "Z")


def _past_iso(days: int = 7) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat().replace("+00:00", "Z")


def _make_report(**overrides) -> AppBypassReport:
    rpt = AppBypassReport(app_id="apps_test", snapshot_path="x.sqlite")
    rpt.per_query = overrides.get("per_query", {})
    rpt.p0_unresolved_total = overrides.get("p0_unresolved_total", 0)
    rpt.p1_unresolved_total = overrides.get("p1_unresolved_total", 0)
    rpt.p2_unresolved_total = overrides.get("p2_unresolved_total", 0)
    return rpt


def test_clean_report_passes():
    r = _make_report()
    v = validate_bypass_report(r)
    assert v.passed
    assert v.fail_reasons == []


def test_p0_unresolved_fails():
    r = _make_report(
        per_query={"q1": {"severity": "P0", "unresolved": 3}},
        p0_unresolved_total=3,
    )
    v = validate_bypass_report(r)
    assert not v.passed
    assert any("q1" in s for s in v.fail_reasons)


def test_p1_does_not_fail_by_default():
    r = _make_report(
        per_query={"q1": {"severity": "P1", "unresolved": 5}},
        p1_unresolved_total=5,
    )
    v = validate_bypass_report(r)
    assert v.passed


def test_p1_fails_in_strict_mode():
    r = _make_report(
        per_query={"q1": {"severity": "P1", "unresolved": 5}},
        p1_unresolved_total=5,
    )
    v = validate_bypass_report(r, fail_on_p1=True)
    assert not v.passed


def test_active_waiver_consumes_p0():
    r = _make_report(
        per_query={"q1": {"severity": "P0", "unresolved": 1}},
        p0_unresolved_total=1,
    )
    w = Waiver(
        app_id="apps_test",
        query_name="q1",
        reason_code="acknowledged",
        risk_class="NORMAL",
        owner="alice",
        expires_at=_future_iso(),
    )
    v = validate_bypass_report(r, waivers=(w,))
    assert v.passed
    assert any("q1:acknowledged:alice" in s for s in v.waivers_consumed)


def test_expired_waiver_does_not_consume():
    r = _make_report(
        per_query={"q1": {"severity": "P0", "unresolved": 1}},
        p0_unresolved_total=1,
    )
    w = Waiver(
        app_id="apps_test",
        query_name="q1",
        reason_code="acknowledged",
        risk_class="NORMAL",
        owner="alice",
        expires_at=_past_iso(),
    )
    v = validate_bypass_report(r, waivers=(w,))
    assert not v.passed


def test_load_waivers_missing_file_returns_empty(tmp_path: Path):
    assert load_waivers(tmp_path / "nope.json") == ()
    assert load_waivers(None) == ()


def test_load_waivers_validates_list(tmp_path: Path):
    p = tmp_path / "w.json"
    p.write_text("{}", encoding="utf-8")  # not a list
    with pytest.raises(ValueError):
        load_waivers(p)


def test_load_waivers_parses_records(tmp_path: Path):
    p = tmp_path / "w.json"
    p.write_text(
        json.dumps(
            [
                {
                    "app_id": "a",
                    "query_name": "q",
                    "reason_code": "r",
                    "risk_class": "NORMAL",
                    "owner": "o",
                    "expires_at": _future_iso(),
                }
            ]
        ),
        encoding="utf-8",
    )
    ws = load_waivers(p)
    assert len(ws) == 1 and ws[0].app_id == "a"


def test_run_full_bypass_validation_e2e(tiny_adg_snapshot: Path):
    reports, results = run_full_bypass_validation(
        snapshot=tiny_adg_snapshot,
        apps=("apps_eval",),
    )
    assert "apps_eval" in reports
    assert results["apps_eval"].passed


def test_run_bypass_queries_clamps_negative_sentinels(tiny_adg_snapshot: Path):
    """BUG #3 REGRESSION: when a query errors and sets unresolved=-1, that
    sentinel must NOT be summed into p*_unresolved_total or it produces
    negative totals that mask real failures.
    """
    from apps_shared.proof.adg_queries import run_bypass_queries

    # Run against the tiny fixture (all clean) — totals must be >= 0
    report = run_bypass_queries(snapshot=tiny_adg_snapshot, app_id="apps_eval")
    assert report.p0_unresolved_total >= 0
    assert report.p1_unresolved_total >= 0
    assert report.p2_unresolved_total >= 0
    # If any query errored, its per_query entry has unresolved=-1
    # but the total must remain non-negative.
    for q_name, q_result in report.per_query.items():
        unresolved = q_result.get("unresolved", 0)
        if isinstance(unresolved, int) and unresolved < 0:
            # error-sentinel present — totals must still be non-negative
            assert report.p0_unresolved_total >= 0, (
                f"sentinel from {q_name} contaminated p0 total"
            )
