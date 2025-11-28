from l3.lic_orchestrator import LICOrchestrator
from l4.lic_state import LICState
from l1.lic_plan_schema import LICPlan

def test_safety_check_stub():
    o = LICOrchestrator()
    state = LICState()
    plan = LICPlan(None,None,None,None,None,None,None,None,None,None)
    result = o.apply_safety_checks(plan, state, message=None)
    # This should be None because method is stubbed.
    assert result is None
