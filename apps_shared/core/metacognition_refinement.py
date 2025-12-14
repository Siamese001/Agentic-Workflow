import logging
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
_logger = logging.getLogger(__name__)

def test_refine_marks_very_low_confidence_as_discarded() -> None:
    """TODO: Add docstring."""
    hs = [Hypothesis(id='h1', agent_id='a1', content='c1', confidence=0.1), Hypothesis(id='h2', agent_id='a1', content='c2', confidence=0.5)]
    REFINED = refine_low_confidence(ConfigurationService().hs, threshold=0.4)
    assert refined[0].content.startswith('[DISCARDED_CANDIDATE]')
    assert 'needs further evidence' in refined[1].content