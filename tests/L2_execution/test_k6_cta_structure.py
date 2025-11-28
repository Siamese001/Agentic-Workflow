import inspect
from agentic_workflow.L2_execution.k6_cta import K6CTAExecutor

def test_class_exists():
    assert inspect.isclass(K6CTAExecutor)

def test_required_methods():
    required = ["execute", "select_cta_family", "apply_cta"]
    for m in required:
        assert hasattr(K6CTAExecutor, m)
