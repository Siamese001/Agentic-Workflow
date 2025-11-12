from src.lic_agentic.qa import MetricsTracker, QAResult


def test_metrics_aggregate_pass_rate_and_latency():
    tracker = MetricsTracker()
    tracker.record(
        QAResult(True, ()),
        latency_ms=1200,
        token_count=120,
        retry_attempted=True,
        retry_succeeded=True,
        token_drift=0.05,
    )
    tracker.record(
        QAResult(False, ("Missing signature",)),
        latency_ms=2000,
        retry_attempted=True,
        retry_succeeded=False,
        token_drift=0.08,
    )
    assert tracker.pass_rate() == 0.5
    assert tracker.latency_p95() == 2000
    assert tracker.average_tokens() == 120.0
    breakdown = tracker.failure_breakdown()
    assert breakdown["Missing signature"] == 1
    assert tracker.retry_success_rate() == 0.5
    assert tracker.token_drift() == 0.08
    tracker.reset()
    assert tracker.pass_rate() == 0.0
    assert tracker.latency_p95() == 0
    assert tracker.average_tokens() == 0.0
    assert tracker.retry_success_rate() == 0.0
    assert tracker.token_drift() == 0.0
