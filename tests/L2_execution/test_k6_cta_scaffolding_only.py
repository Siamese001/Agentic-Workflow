from agentic_workflow.L2_execution.k6_cta import K6CTAExecutor

def test_stub_none_returns():
    k6 = K6CTAExecutor()
    assert k6.execute(None, None) is None
    assert k6.select_cta_family(None) is None
    assert k6.apply_cta(None, None) is None
