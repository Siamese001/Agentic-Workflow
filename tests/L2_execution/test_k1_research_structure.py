import inspect
from agentic_workflow.L2_execution.k1_research import K1ResearchExecutor

def test_class_exists():
    assert inspect.isclass(K1ResearchExecutor)

def test_required_methods():
    required = [
        "execute",
        "run_single_hop",
        "aggregate_results",
        "finalize_research",
    ]
    for m in required:
        assert hasattr(K1ResearchExecutor, m)
