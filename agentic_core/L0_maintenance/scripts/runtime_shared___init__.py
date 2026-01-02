from __future__ import annotations
"""

Shared runtime components for Agentic Workflow.

This is a minimal version to unblock testing while syntax errors are fixed.
"""

# Core SDK Registry - Required for tests
from scripts.runtime.shared.sdk_registry import (
    SDK_REGISTRY,
    SDKCategory,
    SDKEntry,
    get_vector_store,
    reset_all_clients,
    validate_sdk,
)

# Core Models and Exceptions - Temporarily commented out due to Missing imports
# from agentic_core.models import (
#     ReasoningConfig,
#     ValidationResult,
#     HopCheckpoint,
#     RAGState
# )

# Exceptions - Temporarily commented out
# from agentic_core.exceptions import (
#     AgenticWorkflowError,
#     ValidationError,
#     APIError,
#     HopExecutionError
# )

# Configuration - Temporarily commented out

# Basic utilities - Temporarily commented out

# OpenAI Client - Temporarily commented out
# from agentic_core.openai_client import (
#     OpenAIClientManager,
#     get_openai_client,
#     configure_openai,
#     create_agent_prompt,
#     test_openai_connection
# )

__all__ = [
    # SDK Registry
    "SDK_REGISTRY",
    "SDKEntry",
    "SDKCategory",
    "validate_sdk",
    "reset_all_clients",
    "get_vector_store"
]

# Note: The following imports are commented out due to syntax errors:
# - titanium_rag_pipeline.py (syntax errors)
# - titanium_search_tool.py (indentation errors)
# - signal_quality_pipeline.py (syntax errors)
# - adversarial_defense.py (may have issues)
# - corrective_rag.py (may have issues)
# - graphrag_fusion.py (may have issues)
# And many more...
# These will be re-enabled once syntax errors are fixed.
