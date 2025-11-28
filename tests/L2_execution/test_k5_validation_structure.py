import inspect
from agentic_workflow.L2_execution.k5_validation_exec import K5ExecutionValidator

def test_class_exists():
    assert inspect.isclass(K5ExecutionValidator)

def test_required_methods():
    for m in ["execute", "check_structure", "check_semantics"]:
        assert hasattr(K5ExecutionValidator, m)
