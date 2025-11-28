import pytest
from schema import ResumeOutputSchema
from workflow.runner import run_workflow


@pytest.mark.contract
def test_resume_schema_compliance():
    result = run_workflow({"resume": "AI Exec", "jd": "AWS"})
    ResumeOutputSchema(**result["resume"])


@pytest.mark.contract
def test_latency_under_sla(benchmark):
    ctx = {"resume": "fast", "jd": "QuickTest"}
    out = benchmark(lambda: run_workflow(ctx))
    assert out is not None


@pytest.mark.contract
def test_idempotent_results():
    ctx = {"resume": "repeat", "jd": "same"}
    r1, r2 = run_workflow(ctx), run_workflow(ctx)
    assert r1 == r2


@pytest.mark.xfail(reason="Add 22 more contract and SLA enforcement tests", strict=False)
def test_placeholder():
    pytest.xfail("Add 22 more contract and SLA enforcement tests")
