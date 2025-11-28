import inspect
from l2.lic_k6_cta import LIC_K6_CTA

def test_class_exists():
    assert inspect.isclass(LIC_K6_CTA)

def test_required_methods():
    required = ["execute", "generate_date_window", "generate_cta_content"]
    for m in required:
        assert hasattr(LIC_K6_CTA, m)
