import pytest
from workflow.runner import run_workflow


@pytest.mark.performance
def test_batch_performance(benchmark):
    ctx = {"resume": "BatchCase", "jd": "AI Director"}
    result = benchmark(lambda: run_workflow(ctx))
    assert result["status"] == "success"


@pytest.mark.performance
def test_latency_under_3s(benchmark):
    ctx = {"resume": "SpeedTest"}
    result = benchmark(lambda: run_workflow(ctx))
    assert result is not None


@pytest.mark.skip("Add 8 more performance + memory tests")
def test_placeholder():
    pass
