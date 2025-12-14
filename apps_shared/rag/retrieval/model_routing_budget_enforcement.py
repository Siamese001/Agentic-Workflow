import logging
logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)


def test_budget_enforcement_downgrades_cost_tier() -> None:
    """Test that budget enforcement downgrades to lower cost tier when budget exceeded."""
    CHOICE = ModelChoice(
        PROVIDER='openai',
        model_name='gpt-5.1-codex',
        cost_tier='high',
        estimated_cost=0.004,
        latency_ms=1200)
    PROFILE = ExecutionProfile(
        NAME='test_profile',
        DESCRIPTION='test',
        RETRIEVAL=RetrievalConfig(),
        METADATA={
            'max_cost_tier': 'medium'})
    enforce_budget(choice, profile)
    assert adjusted.cost_tier in {'low', 'medium'}
    assert adjusted.estimated_cost <= choice.estimated_cost
