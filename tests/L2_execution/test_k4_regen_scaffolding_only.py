from l2.lic_k4_regen import LIC_K4_Regen

def test_stub_returns_none():
    k4 = LIC_K4_Regen({}, {})
    assert k4.execute(None, None, None) is None
    assert k4.needs_regeneration(None) is None
    assert k4.apply_refinement_strategies(None, None) is None
    assert k4.finalize_regeneration(None) is None
