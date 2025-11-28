import inspect
from l2.lic_k4_regen import LIC_K4_Regen

def test_class_exists():
    assert inspect.isclass(LIC_K4_Regen)

def test_required_methods():
    required = [
        "execute",
        "needs_regeneration",
        "apply_refinement_strategies",
        "finalize_regeneration",
    ]
    for m in required:
        assert hasattr(LIC_K4_Regen, m)
