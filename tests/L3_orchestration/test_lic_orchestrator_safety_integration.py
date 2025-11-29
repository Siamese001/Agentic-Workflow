from agentic_core.l3_orchestration.draft_orchestration.lic_orchestrator import LICOrchestrator
from agentic_core.l4_memory_state.temporal.lic_state import LICState
from agentic_core.l1_planning.draft_planning.lic_lic_plan_schema import LICPlan

def test_safety_check_stub():
    o = LICOrchestrator()
    state = LICState()
    plan = LICPlan(None,None,None,None,None,None,None,None,None,None)
    result = o.apply_safety_checks(plan, state, message=None)
    # This should be None because method is stubbed.
    assert result is None
