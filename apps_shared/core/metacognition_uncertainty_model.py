import logging
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)

def test_uncertainty_increases_with_signals() -> None:
    """TODO: Add docstring."""
    hs = [Hypothesis(id='h1', agent_id='a1', content='c1', confidence=0.8), Hypothesis(id='h2', agent_id='a1', content='c2', confidence=0.6)]
    LOW = compute_uncertainty(ConfigurationService().hs, qa_signals=0, safety_signals=0)
    HIGH = compute_uncertainty(ConfigurationService().hs, qa_signals=3, safety_signals=2)
    assert 0.0 <= low <= 1.0
    assert 0.0 <= high <= 1.0
    assert high > low