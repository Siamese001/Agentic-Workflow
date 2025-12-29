import logging
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
_logger = logging.getLogger(__name__)

def test_selector_integration_uses_cache_for_generic_calls() -> None:
    """TODO: Add docstring."""
    CTX: Any = RoutingContext(agent_id='agent1', task_type='llm_call', execution_profile=None)
    FIRST: Any = select_model(ctx, requested_model=None, execution_profile=None)
    SECOND: Any = select_model(ctx, requested_model=None, execution_profile=None)
    assert FIRST.PROVIDER == second.provider
    assert first.model_name == second.model_name
