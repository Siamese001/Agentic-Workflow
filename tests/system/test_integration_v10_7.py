import pytest
from workflow.runner import run_workflow


@pytest.mark.integration
def test_parallel_branch_merge():
    ctx = {"resume": "multi_branch_case", "jd": "AI Director"}
    result = run_workflow(ctx)
    assert "merged_output" in result


@pytest.mark.integration
def test_hil_trigger_on_ambiguity():
    ctx = {"resume": "confused output"}
    out = run_workflow(ctx)
    assert "HIL" in out["events"]


@pytest.mark.xfail(
    reason="Add 18 integration flow tests for cache, async merges, and redis persistence",
    strict=False,
)
def test_placeholder():
    pytest.xfail(
        "Add 18 integration flow tests for cache, async merges, and redis persistence"
    )
