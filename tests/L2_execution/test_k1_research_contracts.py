from l2.lic_k1_research import LIC_K1_Research

def test_constructor():
    k1 = LIC_K1_Research({})
    assert isinstance(k1, LIC_K1_Research)

def test_execute_signature():
    k1 = LIC_K1_Research({})
    result = k1.execute(recipient=None, message_context=None)
    assert result is None
