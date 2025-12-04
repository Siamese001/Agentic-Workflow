import pytest
from workflow.runner import run_workflow
from schema import ResumeOutputSchema

@pytest.mark.parametrize("jd", ["AWS","Anthropic","Databricks","CoreWeave","Citi"])
def test_resume_schema_compliance(jd):
    out = run_workflow({"resume":"AI Exec", "jd": jd})
    ResumeOutputSchema(**out["resume"])  # raises if invalid

@pytest.mark.parametrize("repeat", [1,2,3,4,5])
def test_idempotency(repeat):
    ctx={"resume":"repeatable","jd":"same"}
    outs=[run_workflow(ctx) for _ in range(repeat)]
    assert all(o==outs[0] for o in outs)
