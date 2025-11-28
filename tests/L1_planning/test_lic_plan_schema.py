from agentic_workflow.L1_planning.lic_plan_schema import LICPlan

def test_schema_initialization():
    p = LICPlan(1,2,3,4,5,6,7,8,9,10)
    assert p.message_type == 1
    assert p.cta_style == 9
    assert p.assembly_plan == 10
