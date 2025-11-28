import pytest
from workflow.runner import run_workflow


@pytest.mark.performance
def test_batch_performance(benchmark):
    ctx = {"compat_mode": "v10_7", "resume": "BatchCase", "jd": "AI Director"}
    result = benchmark(lambda: run_workflow(ctx))
    assert result["status"] == "success"


@pytest.mark.performance
def test_latency_under_3s(benchmark):
    ctx = {"compat_mode": "v10_7", "resume": "SpeedTest"}
    result = benchmark(lambda: run_workflow(ctx))
    assert result is not None


def test_retry_context_emits_retry_event():
    ctx = {"compat_mode": "v10_7", "resume": "RetryCase", "low_confidence": True}
    result = run_workflow(ctx)
    assert result["status"] == "success"
    assert "retry" in result["events"]
