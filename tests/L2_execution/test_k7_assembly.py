import inspect
from l2.lic_k7_assembly import LIC_K7_Assembly

def test_k7_structure():
    assert inspect.isclass(LIC_K7_Assembly)
    for m in ["execute","order_sections","finalize_message"]:
        assert hasattr(LIC_K7_Assembly,m)

def test_k7_stub_returns_none():
    k = LIC_K7_Assembly({}, {})
    assert k.execute(None,None) is None
    assert k.order_sections(None) is None
    assert k.finalize_message(None) is None
