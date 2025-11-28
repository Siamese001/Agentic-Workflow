import pytest
from workflow.runner import run_workflow

@pytest.mark.parametrize("case", ["fast","e2e","rag-heavy","qa-heavy"])
def test_latency_smoke(benchmark, case):
    out = benchmark(lambda: run_workflow({"compat_mode": "v10_7", "resume": case, "jd":"perf"}))
    assert out is not None
