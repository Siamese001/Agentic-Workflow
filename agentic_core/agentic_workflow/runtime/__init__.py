"""

logger = logging.getLogger(__name__)
Runtime components for Agentic Workflow.

This module provides runtime logic, shared utilities, and core functionality
for the agentic workflow system.
"""

# Import shared components from the actual location
import sys
from pathlib import Path

# Add the actual runtime directories to Python path
runtime_path = Path(__file__).parent.parent.parent / "03_runtime"
shared_path = runtime_path / "shared"

if str(runtime_path) not in sys.path:
    sys.path.insert(0, str(runtime_path))
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))

# Import and re-export shared components
try:
    pass


    __all__ = [
        "OpenAIClientManager",
        "get_openai_client",
        "configure_openai",
        "create_agent_prompt",
        "test_openai_connection",
        "SDK_REGISTRY",
        "SDKEntry",
        "SDKCategory",
        "validate_sdk",
        "reset_all_clients",
        "get_vector_store",
        "get_redis_client"
    ]
except ImportError as e:
    logger.warning(f"Warning: Could not import runtime components: {e}")
    __all__ = []
