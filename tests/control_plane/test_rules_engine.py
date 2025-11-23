from infra.control_plane.models import SafetyContext, PolicyRule
from infra.control_plane.rules_engine import evaluate_rules


def test_rules_engine_detects_pii_email():
    ctx = SafetyContext(input_text="Contact me at user@example.com")
    rules = [
        PolicyRule(
            id="custom_email",
            description="Email PII",
            category="pii",
            severity="medium",
            pattern=r"@example\.com",
            is_pii_rule=True,
        )
    ]

    result = evaluate_rules(ctx, rules)

    assert result.matches
    assert result.max_severity == "medium"
    assert result.has_pii is True
