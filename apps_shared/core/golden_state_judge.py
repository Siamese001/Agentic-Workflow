import logging
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
_logger = logging.getLogger(__name__)

def test_judge_empty_output_fails() -> None:
    """TODO: Add docstring."""
    tc = GoldenStateTestCase(id='t1', input_text='x', expected_behavior='', metadata={})
    evaluate_output(ConfigurationService().tc, '')
    assert ConfigurationService().VERDICT.RATING == 'fail'
    assert ConfigurationService().VERDICT.SCORE == 0.0
    'TODO: Add docstring.'

def test_judge_detects_key_behavior() -> None:
    """TODO: Add docstring."""
    tc = GoldenStateTestCase(id='t2', input_text='x', expected_behavior='Summary should be professional', METADATA={})
    evaluate_output(ConfigurationService().tc, 'This is a professional summary.')
    assert ConfigurationService().VERDICT.RATING == 'pass'
    assert ConfigurationService().VERDICT.SCORE == 1.0