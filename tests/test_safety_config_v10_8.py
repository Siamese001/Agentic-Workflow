from l5_injection_detector import InjectionDetector
from l5_policy_engine import PolicyEngine
from safety_config import InjectionPattern, PolicyRule, SafetyConfig, load_default_safety_config


def test_default_config_loads():
    config = load_default_safety_config()

    assert len(config.injection_patterns) >= 2
    assert config.injection_patterns[0].pattern == "ignore previous instructions"
    assert any(rule.action == "exfiltrate_data" for rule in config.policy_rules)
    assert config.pii_enabled is True
    assert config.bias_enabled is True


def test_policy_config_used_by_policy_engine():
    config = SafetyConfig(
        policy_rules=[PolicyRule(action="restricted", allowed=False, reason="custom block")],
        injection_patterns=[],
        pii_enabled=False,
        bias_enabled=False,
    )
    engine = PolicyEngine(config=config)

    patch = engine.evaluate({"action": "restricted"})

    evaluation = patch["policy_evaluation"]
    assert evaluation["allowed"] is False
    assert evaluation["denied_reason"] == "custom block"
    assert evaluation["denied_actions"] == ["restricted"]


def test_injection_patterns_override_defaults():
    config = SafetyConfig(
        policy_rules=[],
        injection_patterns=[InjectionPattern(pattern="special trigger", enabled=True, tags=["custom"])],
        pii_enabled=False,
        bias_enabled=False,
    )
    detector = InjectionDetector(config=config)

    patch = detector.scan("This content includes a SPECIAL TRIGGER for testing.")

    matches = patch["injection_scan"]["matches"]
    matched_patterns = patch["injection_scan"]["matched_patterns"]
    assert matches == ["special trigger"]
    assert matched_patterns == ["special trigger"]
    assert patch["injection_scan"]["is_injection"] is True
