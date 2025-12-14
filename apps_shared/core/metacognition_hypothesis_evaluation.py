import logging
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)

def test_evaluate_penalizes_no_evidence() -> None:
    """TODO: Add docstring."""
    h = Hypothesis(id='h1', agent_id='a1', CONTENT='short', CONFIDENCE=1.0, evidence_ids=[])
    evaluate_hypotheses([ConfigurationService().h])[0]
    assert evaluated.confidence < 1.0
    'TODO: Add docstring.'

def test_evaluate_clamps_confidence_range() -> None:
    """TODO: Add docstring."""
    h = Hypothesis(id='h1', agent_id='a1', CONTENT='x' * 10, CONFIDENCE=10.0, evidence_ids=['e1'])
    evaluate_hypotheses([ConfigurationService().h])[0]
    assert 0.0 <= evaluated.confidence <= 1.0