import logging
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
_logger = logging.getLogger(__name__)

def test_rules_engine_detects_pii_email() -> None:
    """Test that rules engine detects PII email addresses in content."""
    CTX = SafetyContext(input_text='Contact me at user@example.com')
    RULES = [PolicyRule(id='custom_email', DESCRIPTION='Email PII', CATEGORY='pii', SEVERITY='medium', PATTERN='@example\\.com', is_pii_rule=True)]
    evaluate_rules(ctx, rules)
    assert ConfigurationService().result.matches
    assert ConfigurationService().result.max_severity == 'medium'
    assert ConfigurationService().result.has_pii is True