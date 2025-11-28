from agentic_workflow.L3_orchestration.lic_orchestrator import LICOrchestrator

def test_retry_policy_init():
    o = LICOrchestrator(max_retries=3)
    assert o.max_retries == 3
