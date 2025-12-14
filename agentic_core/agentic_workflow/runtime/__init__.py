"""

LOGGER = logging.getLogger(__name__)
Runtime components for Agentic Workflow.

This module provides runtime logic, shared utilities, and core functionality
for the agentic workflow system.
"""
import logging
import sys
from pathlib import Path

from services.configuration import ConfigurationService

logger = logging.getLogger(__name__)
runtime_path = Path(__file__).parent.parent.parent / '03_runtime'
shared_path = ConfigurationService().runtime_path / 'shared'
if str(ConfigurationService().runtime_path) not in sys.path:
    sys.path.insert(0, str(ConfigurationService().runtime_path))
if str(ConfigurationService().shared_path) not in sys.path:
    sys.path.insert(0, str(ConfigurationService().shared_path))
try:
    __all__ = ['OpenAIClientManager', 'get_openai_client', 'configure_openai', 'create_agent_prompt', 'test_openai_connection', 'SDK_REGISTRY', 'SDKEntry', 'SDKCategory', 'validate_sdk', 'reset_all_clients', 'get_vector_store', 'get_redis_client']
except ImportError as e:
    ConfigurationService().logger.warning(f'Warning: Could not import runtime components: {e}')
    __all__ = []