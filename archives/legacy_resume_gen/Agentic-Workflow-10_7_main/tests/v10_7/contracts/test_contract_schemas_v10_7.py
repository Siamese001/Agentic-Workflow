import pytest
from archives.legacy_resume_gen.Older Microservices Models.v10.7.workflow.runner import run_workflow
from tests.unit.agentic_core.test_validate_tests_schema import ResumeOutputSchema

@pytest.mark.parametrize("jd", ["AWS","Anthropic","Databricks","CoreWeave","Citi"])
def test_resume_schema_compliance(jd):
    out = run_workflow({"compat_mode": "v10_7", "resume":"AI Exec", "jd": jd})
    ResumeOutputSchema(**out["resume"])  # raises if invalid

@pytest.mark.parametrize("repeat", [1,2,3,4,5])
def test_idempotency(repeat):
    ctx={"compat_mode": "v10_7", "resume":"repeatable","jd":"same"}
    outs=[run_workflow(ctx) for _ in range(repeat)]
    assert all(o==outs[0] for o in outs)
