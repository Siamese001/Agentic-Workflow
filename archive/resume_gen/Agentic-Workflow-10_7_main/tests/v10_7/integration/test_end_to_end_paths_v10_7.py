import pytest
from workflow.runner import run_workflow

@pytest.mark.parametrize("resume,jd,expect_keys", [
    ("Jane Doe","Chief AI Officer", ["summary"]),
    ("John Smith","Director, AI", ["summary"]),
    ("LowConf","Analyst", ["events"]),
    ("Ambiguous","Unknown", ["events"]),
])
def test_full_run_variants(resume,jd,expect_keys):
    out = run_workflow({"compat_mode": "v10_7", "resume": resume, "jd": jd})
    for k in expect_keys: assert k in out

@pytest.mark.parametrize("scenario", ["batch-small","batch-large","parallel-merge","hil-trigger"])
def test_scenarios_collectively(scenario):
    out = run_workflow({"compat_mode": "v10_7", "resume": scenario, "jd":"scenario"})
    assert isinstance(out, dict)
