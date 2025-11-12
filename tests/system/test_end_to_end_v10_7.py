import pytest
from workflow.runner import run_workflow


@pytest.mark.integration
def test_full_resume_generation_pipeline():
    ctx = {"resume": "Jane Doe", "jd": "Chief AI Officer"}
    output = run_workflow(ctx)
    assert output["status"] == "success"
    assert "summary" in output


@pytest.mark.integration
def test_ambiguity_triggers_tot_branching():
    ctx = {"resume": "ambiguous input"}
    out = run_workflow(ctx)
    assert "ToT" in out["events"]


@pytest.mark.integration
def test_low_confidence_triggers_retry():
    ctx = {"resume": "low_confidence_case"}
    out = run_workflow(ctx)
    assert "retry" in out["events"]


@pytest.mark.skip("Add 17 more integration tests for all stacks")
def test_placeholder():
    pass
