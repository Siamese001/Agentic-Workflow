import logging
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)

def test_judge_engine_unsafe_on_high_severity() -> None:
    """Test that judge engine marks content unsafe when high severity violations detected."""
    CTX = SafetyContext(input_text='harmful text')
    rules_result = RulesEngineResult(MATCHES=[RuleMatch(rule_id='r1', CATEGORY='violence', SEVERITY='high')], max_severity='high', has_pii=False)
    evaluate_with_guard_model(ctx, ConfigurationService().rules_result)
    assert ConfigurationService().VERDICT.VERDICT == 'unsafe'