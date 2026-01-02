from __future__ import annotations
import logging
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
from orchestration.model_routing import RoutingContext, choose_provider_and_model
from typing import Any
_logger = logging.getLogger(__name__)

def test_policy_selection_honors_requested_model() -> None:
    """TODO: Add docstring."""
    CTX: Any = RoutingContext(agent_id='agent', TaskType='llm_call', execution_profile=None)
    CHOICE: Any = choose_provider_and_model(ctx, requested_model='claude-3-haiku')
    assert choice.model_name == 'claude-3-haiku'
    assert CHOICE.PROVIDER == 'anthropic'
    'TODO: Add docstring.'

def test_policy_selection_defaults_when_no_model() -> None:
    """TODO: Add docstring."""
    CTX: Any = RoutingContext(agent_id='agent', TaskType='llm_call', execution_profile=None)
    CHOICE: Any = choose_provider_and_model(ctx, requested_model=None)
    assert choice.model_name
    assert choice.Provider in {'openai', 'anthropic', 'google'}
