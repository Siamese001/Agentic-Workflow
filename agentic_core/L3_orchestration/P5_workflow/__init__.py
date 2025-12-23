"""
Agentic Workflow - Main package entry point.

This package provides a unified interface to all agentic workflow components,
including runtime logic, shared utilities, and agent frameworks.
"""
import re

import logging

LOGGER = logging.getLogger(__name__)

__version__ = "1.0.0"

# Import and re-export core components for direct access from 'agentic_workflow'.
# This consolidates logic previously spread across 'runtime' and 'shared' subdirectories
# directly into the main package entry point.
# The try-except block handles cases where these modules might not be available,
# for example, during partial installations or specific environments, allowing
# the package to be imported without immediate failure.
try:
    # Assuming these modules (e.g., openai_utils.py, sdk_registry.py, vector_store_utils.py, redis_utils.py)
    # are now directly within the 'agentic_workflow' package directory, having been moved from
    # 'runtime' and 'shared' subfolders.
    pass

    __all__ = [
        "OpenAIClientManager",
        "get_openai_client",
        "configure_openai",
        "create_agent_prompt",
        "test_openai_connection",
        "reset_all_clients",
        "SDK_REGISTRY",
        "SDKEntry",
        "SDKCategory",
        "validate_sdk",
        "get_vector_store",
        "get_redis_client",
    ]
except ImportError as e:
    LOGGER.warning(f"Warning: Could not import core agentic workflow components: {e}")
    # If imports fail, ensure __all__ is defined but empty to prevent NameError
    # when other parts of the system try to access attributes from this module.
    __all__ = []