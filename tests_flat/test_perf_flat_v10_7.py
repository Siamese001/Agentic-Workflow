# AUTO-GENERATED FLAT TEST FILE
# Sources:
#   - tests/integration/test_perf_latency_v10_7.py
#   - tests/integration/test_sla_latency_v10_7.py
# ------------------------------------------------------------------
# ----- BEGIN: tests/integration/test_perf_latency_v10_7.py -----
import pytest
from workflow.runner import run_workflow

@pytest.mark.parametrize("case", ["fast","e2e","rag-heavy","qa-heavy"])
def test_latency_smoke(benchmark, case):
    out = benchmark(lambda: run_workflow({"resume": case, "jd":"perf"}))
    assert out is not None
# ----- END: tests/integration/test_perf_latency_v10_7.py -----
# ----- BEGIN: tests/integration/test_sla_latency_v10_7.py -----
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


def test_retry_context_emits_retry_event():
    ctx = {"resume": "RetryCase", "low_confidence": True}
    result = run_workflow(ctx)
    assert result["status"] == "success"
    assert "retry" in result["events"]
# ----- END: tests/integration/test_sla_latency_v10_7.py -----
