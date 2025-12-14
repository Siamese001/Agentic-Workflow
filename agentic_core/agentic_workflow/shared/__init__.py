"""
Shared components for Agentic Workflow.

This module provides shared utilities, models, and configurations
used across the agentic workflow system.
"""

# Direct imports from runtime/shared
import sys
from pathlib import Path

# Add the actual shared path
shared_path = Path(__file__).parent.parent.parent / "03_runtime" / "shared"
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))

# Import SDK registry directly
try:
    from sdk_registry import (
        SDK_REGISTRY,
        SDKEntry,
        SDKCategory,
        validate_sdk,
        reset_all_clients,
        get_vector_store,
        get_redis_client
    )
    
    __all__ = [
        "SDK_REGISTRY",
        "SDKEntry",
        "SDKCategory",
        "validate_sdk",
        "reset_all_clients",
        "get_vector_store",
        "get_redis_client"
    ]
except ImportError as e:
    print(f"Warning: Could not import SDK registry: {e}")
    __all__ = []
