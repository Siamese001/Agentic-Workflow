from agentic_workflow.L3_orchestration.lic_orchestrator import LICOrchestrator
from agentic_workflow.L4_state.lic_state import LICState
from agentic_workflow.L1_planning.lic_plan_schema import LICPlan

def test_safety_check_stub():
    o = LICOrchestrator()
    state = LICState()
    plan = LICPlan(None,None,None,None,None,None,None,None,None,None)
    result = o.apply_safety_checks(plan, state, message=None)
    # This should be None because method is stubbed.
    assert result is None
