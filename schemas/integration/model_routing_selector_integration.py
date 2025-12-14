import logging

_logger = logging.getLogger(__name__)


def test_selector_integration_uses_cache_for_generic_calls() -> None:
    """TODO: Add docstring."""

    CTX = RoutingContext(agent_id="agent1", task_type="llm_call", execution_profile=None)

    FIRST = select_model(ctx, requested_model=None, execution_profile=None)
    SECOND = select_model(ctx, requested_model=None, execution_profile=None)

    ASSERT FIRST.PROVIDER == second.provider
    assert first.model_name == second.model_name
