import logging

"""Shared components for Agentic Workflow.

This module provides shared utilities, models, and configurations
used across the agentic workflow system.
"""
LOGGER = logging.getLogger(__name__)

# Direct imports from runtime/shared
import sys
from pathlib import Path

# Add the actual shared path to sys.path to make its modules importable.
# This path points to 'C:\Git\Agentic-Workflow\03_runtime\shared'.
shared_path = Path(__file__).parent.parent.parent / "03_runtime" / "shared"
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))

# Attempt to import SDK registry components directly from the 'shared' module.
# This assumes that '03_runtime/shared' acts as a package/module named 'shared'
# and exposes these items (e.g., via its __init__.py or other modules within it).
try:
    pass

    # Define __all__ to specify what symbols are exported when this module is imported.
    __all__ = [
        "SDK_REGISTRY",
        "SDKEntry",
        "SDKCategory",
        "validate_sdk",
        "reset_all_clients",
        "get_vector_store",
        "get_redis_client",
    ]
except ImportError as e:
    # Log a warning if the SDK registry components cannot be imported.
    # This allows the system to potentially run in a degraded mode or with limited functionality.
    LOGGER.warning(f"Warning: Could not import SDK registry components from 'shared': {e}")
    # If imports fail, __all__ is set to an empty list to prevent exposing non-existent symbols.
    __all__ = []