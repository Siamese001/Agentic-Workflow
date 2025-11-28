from l4.lic_state import LICState

def test_state_structure():
    s = LICState()
    assert hasattr(s,"k_node_outputs")
    assert hasattr(s,"violations")

def test_state_stub_methods():
    s = LICState()
    assert s.record_output("k1",None) is None
    assert s.record_violation("v") is None
