import inspect
from agentic_workflow.L2_execution.k2_insights import K2InsightExecutor

def test_class_exists():
    assert inspect.isclass(K2InsightExecutor)

def test_required_methods():
    required = [
        "execute",
        "select_insight_templates",
        "extract_key_points",
        "assemble_insights",
    ]
    for m in required:
        assert hasattr(K2InsightExecutor, m)
