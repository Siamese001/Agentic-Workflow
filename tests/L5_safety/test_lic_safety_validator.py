from agentic_core.l5_safety.safety_validator.safety_validator.safety_validator.lic_safety_validator import LICSafetyValidator

def test_safety_validator_exists():
    s = LICSafetyValidator()
    assert hasattr(s,"validate")
    assert hasattr(s,"classify_violations")

def test_safety_stub_none_returns():
    s = LICSafetyValidator()
    assert s.validate(None,None) is None
    assert s.classify_violations(None) is None





