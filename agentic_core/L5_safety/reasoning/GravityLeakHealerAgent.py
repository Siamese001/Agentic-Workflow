"""GravityLeakHealerAgent - canonical healer name alias for GravityLeakRepairAgent."""

from agentic_core.L5_safety.reasoning.GravityLeakRepairAgent import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    GravityLeakRepairAgent as GravityLeakHealerAgent,
)

__all__ = ["GravityLeakHealerAgent"]
