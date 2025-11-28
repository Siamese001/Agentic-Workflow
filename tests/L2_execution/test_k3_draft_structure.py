import inspect
from l2.lic_k3_draft import LIC_K3_Draft

def test_class_exists():
    assert inspect.isclass(LIC_K3_Draft)

def test_required_methods():
    for m in ["execute", "generate_greeting", "generate_subject_line", "apply_tone_adaptation"]:
        assert hasattr(LIC_K3_Draft, m)
