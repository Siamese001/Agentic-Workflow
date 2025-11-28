from agentic_workflow.L2_execution.k4_regen import K4RegenerationExecutor

def test_constructor():
    k4 = K4RegenerationExecutor()
    assert isinstance(k4, K4RegenerationExecutor)

def test_execute_signature():
    k4 = K4RegenerationExecutor()
    result = k4.execute(plan=None, message=None, safety_feedback=None)
    assert result is None
