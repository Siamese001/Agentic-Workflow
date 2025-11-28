from l2.lic_k6_cta import LIC_K6_CTA

def test_stub_none_returns():
    k6 = LIC_K6_CTA({})
    assert k6.execute(None, None) is None
    assert k6.generate_date_window() is None
    assert k6.generate_cta_content(None, None) is None
