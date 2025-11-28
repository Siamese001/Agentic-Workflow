from l4.lic_memory import LICMemory

def test_memory_structure():
    m = LICMemory()
    assert hasattr(m,"load_sender_profile")
    assert hasattr(m,"save_state_snapshot")

def test_memory_stub_returns_none():
    m = LICMemory()
    assert m.load_sender_profile() is None
    assert m.save_state_snapshot(None) is None
