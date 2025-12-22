```python
import logging
import sys
from pathlib import Path


LOGGER = logging.getLogger(__name__)
"""
Runtime components for Agentic Workflow.

This module provides runtime logic, shared utilities, and core functionality
for the agentic workflow system.
"""


# Add internal runtime directories to Python's import path.
# This allows modules within '03_runtime' and '03_runtime/shared' to be imported
# directly (e.g., `from openai_utils import ...`) as if they were top-level
# modules within the 'agentic_workflow' package. This simplifies internal
# imports by avoiding deeply nested relative imports.
runtime_path = Path(__file__).parent.parent.parent / "03_runtime"
shared_path = runtime_path / "shared"

if str(runtime_path) not in sys.path:
    sys.path.insert(0, str(runtime_path))
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))


# Import and re-export shared components for direct access from 'agentic_workflow.runtime'.
# The try-except block handles cases where these modules might not be available,
# for example, during partial installations or specific environments, allowing
# the package to be imported without immediate failure.
try:
    # These modules are expected to be found directly under the paths added to sys.path.
    from openai_utils import (
        OpenAIClientManager,
        get_openai_client,
        configure_openai,
        create_agent_prompt,
        test_openai_connection,
        reset_all_clients,
    )
    from sdk_registry import SDK_REGISTRY, SDKEntry, SDKCategory, validate_sdk
    from vector_store_utils import get_vector_store
    from redis_utils import get_redis_client

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
    LOGGER.warning(f"Warning: Could not import runtime components: {e}")
    # If imports fail, ensure __all__ is defined but empty to prevent NameError
    # when other parts of the system try to access attributes from this module.
    __all__ = []

```