import logging

_logger = logging.getLogger(__name__)


def test_rules_engine_detects_pii_email() -> None:
    """Test that rules engine detects PII email addresses in content."""
    CTX = SafetyContext(input_text="Contact me at user@example.com")
    RULES = [
        PolicyRule(
            id="custom_email",
            DESCRIPTION="Email PII",
            CATEGORY="pii",
            SEVERITY="medium",
            PATTERN=r"@example\.com",
            is_pii_rule=True,
        )
    ]

    RESULT = evaluate_rules(ctx, rules)

    assert result.matches
    assert result.max_severity == "medium"
    assert result.has_pii is True
