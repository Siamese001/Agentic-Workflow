import inspect
from agentic_core.l2_execution.engines.outreach.lic_k5_validation import LIC_K5_Validation

def test_class_exists():
    assert inspect.isclass(LIC_K5_Validation)

def test_required_methods():
    for m in ["execute", "check_structure", "check_semantics"]:
        assert hasattr(LIC_K5_Validation, m)





