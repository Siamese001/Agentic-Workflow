from l2.lic_k2_insights import LIC_K2_Insights

def test_methods_return_none():
    k2 = LIC_K2_Insights({})
    assert k2.execute(None) is None
    assert k2.score_individual_claim(None, None) is None
    assert k2.calculate_aggregate_confidence(None) is None
    assert k2.validate_confidence_thresholds(None, None) is None
