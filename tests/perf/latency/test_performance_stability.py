"""Performance stability tests - legacy workflow runner."""

import pytest

# TODO: Implement legacy workflow runner (zombie file)
# from archives.legacy_resume_gen.Older Microservices Models.v10.7.workflow.runner import run_workflow

@pytest.mark.skip(reason="Waiting for legacy workflow runner implementation")
@pytest.mark.parametrize("case", ["fast","e2e","rag-heavy","qa-heavy"])
def test_latency_smoke(benchmark, case):
    # out = benchmark(lambda: run_workflow({"resume": case, "jd":"perf"}))
    # assert out is not None
    pass
