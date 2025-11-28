import inspect
from l3.lic_orchestrator import LICOrchestrator

def test_orchestrator_class_exists():
    assert inspect.isclass(LICOrchestrator)

def test_required_methods_exist():
    methods = [
        "run", "run_k1", "run_k2", "run_k3", "run_k4",
        "run_k5", "run_k6", "run_k7",
        "apply_safety_checks", "should_retry"
    ]
    for m in methods:
        assert hasattr(LICOrchestrator, m)
