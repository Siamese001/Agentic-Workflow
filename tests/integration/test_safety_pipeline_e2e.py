import pytest

from models import MainGraphState

try:  # Optional depending on build exposure
    from agent_orchestration_v10_7 import build_workflow

    HAS_WORKFLOW = True
except ImportError:  # pragma: no cover - guard until workflow factory is available
    HAS_WORKFLOW = False


@pytest.mark.skipif(not HAS_WORKFLOW, reason="Workflow builder not available")
def test_safety_fields_populate_in_simple_run():
    initial = MainGraphState()
    workflow = build_workflow(debug_mode=False)

    result_state = workflow.invoke(initial)

    assert hasattr(result_state, "safety_report")
    assert hasattr(result_state, "policy_decision")
    assert hasattr(result_state, "constitutional_review")
