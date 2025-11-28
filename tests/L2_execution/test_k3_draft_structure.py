import inspect
from agentic_workflow.L2_execution.k3_draft import K3DraftExecutor

def test_class_exists():
    assert inspect.isclass(K3DraftExecutor)

def test_required_methods():
    for m in ["execute", "apply_tone_rules", "apply_structure"]:
        assert hasattr(K3DraftExecutor, m)
