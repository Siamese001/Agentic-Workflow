from l2.lic_k5_validation import LIC_K5_Validation

def test_stub_none_returns():
    k5 = LIC_K5_Validation({}, {})
    assert k5.execute(None, None, None, None) is None
    assert k5.check_structure(None) is None
    assert k5.check_semantics(None) is None
