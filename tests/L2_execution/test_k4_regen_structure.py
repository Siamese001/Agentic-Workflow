import inspect
from agentic_workflow.L2_execution.k4_regen import K4RegenerationExecutor

def test_class_exists():
    assert inspect.isclass(K4RegenerationExecutor)

def test_required_methods():
    required = [
        "execute",
        "needs_regeneration",
        "apply_refinement_strategies",
        "finalize_regeneration",
    ]
    for m in required:
        assert hasattr(K4RegenerationExecutor, m)
