from __future__ import annotations

from apps_rg.runtime.observability.trace_trend import build_l6_trace_observability_trend


def test_trace_trend_is_advisory_and_bounded() -> None:
    rows = [
        {"trace_verdict": "TRACE_RECONCILED", "provider_attempt_mirror_status": "PASS", "x3_mirror_status": "PASS"},
        {"trace_verdict": "TRACE_MISMATCH", "provider_attempt_mirror_status": "FAIL", "x3_mirror_status": "FAIL"},
        {"trace_verdict": "TRACE_UNAVAILABLE", "provider_attempt_mirror_status": "WARN", "x3_mirror_status": "WARN"},
    ]
    trend = build_l6_trace_observability_trend(rows, window_size=2)
    assert trend["runs_seen"] == 2
    assert trend["trace_mismatch_count"] == 1
    assert trend["trace_unavailable_count"] == 1
    assert trend["threshold_state"] == "WATCH"
    assert trend["current_run_blocking"] is False
    assert trend["future_run_only"] is True


def test_trace_trend_requires_positive_window() -> None:
    try:
        build_l6_trace_observability_trend([], window_size=0)
    except ValueError as exc:
        assert "window_size" in str(exc)
    else:
        raise AssertionError("expected ValueError")
