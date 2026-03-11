"""
LIC Core Mixins - Re-exports for LIC Sovereign Architecture agents.

Provides convenient access to sovereign mixins for LIC agent consolidation.
"""

from __future__ import annotations

from agentic_core.mixins.healer_mixin import HealerMixin
from agentic_core.mixins.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

__all__ = [
    "SubatomicTestingMixin",
    "MCPHardenedMixin",
    "HealerMixin",
]
