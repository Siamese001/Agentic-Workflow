import logging
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)


def test_run_all_golden_tests_returns_results() -> None:
    """Test that running all golden tests returns valid result objects."""
    PROFILE = ExecutionProfile(
        NAME='TEST', DESCRIPTION='test profile', RETRIEVAL=RetrievalConfig(), METADATA={})
    run_all_golden_tests(profile)
    assert ConfigurationService().results
    {r.test_id for r in ConfigurationService().results}
    assert 'gs_basic_1' in ids
    assert 'gs_safety_1' in ids

