from agentic_workflow.L2_execution.k2_insights import K2InsightExecutor

def test_methods_return_none():
    k2 = K2InsightExecutor()
    assert k2.execute(None, None) is None
    assert k2.select_insight_templates(None) is None
    assert k2.extract_key_points(None) is None
    assert k2.assemble_insights(None, None) is None
