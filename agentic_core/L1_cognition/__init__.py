"""L1 Cognition Layer — Propose-only cognitive processing.

This layer provides cognitive processing, pattern recognition, and reasoning.
No execution, routing, or persistence logic belongs in this layer.
Only cognitive interfaces, reasoning engines, and telemetry are exported.
"""

# Cognitive interfaces and reasoning
from .types.action_request_types import (  # noqa: F401
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    ActionRequest,
    ActionResult,
    PlanningRequest,
    PlanningResult,
)

__all__ = [
    "ActionRequest",
    "ActionResult",
    "PlanningRequest",
    "PlanningResult",
]

# Sovereignty assertion: This layer contains NO execution or routing logic
# L1 may only propose actions; execution belongs to L2, routing to L3
