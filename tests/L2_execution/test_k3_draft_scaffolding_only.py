from l2.lic_k3_draft import LIC_K3_Draft

def test_stub_returns_none():
    k3 = LIC_K3_Draft({}, {})
    assert k3.execute(None, None, None) is None
    assert k3.generate_greeting(None) is None
    assert k3.generate_subject_line(None, None, None) is None
