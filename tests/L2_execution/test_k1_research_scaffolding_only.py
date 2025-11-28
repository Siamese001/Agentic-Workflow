from agentic_workflow.L2_execution.k1_research import K1ResearchExecutor

def test_stub_returns_none():
    k1 = K1ResearchExecutor()
    assert k1.execute(None, None) is None
    assert k1.run_single_hop(None) is None
    assert k1.aggregate_results(None) is None
    assert k1.finalize_research(None) is None
