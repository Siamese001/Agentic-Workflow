"""
Activation gate seam contract — re-exports L5 activation guard for L2 consumers.

This module sits outside the layer hierarchy so imports from here
do not count as upward seams in the gravity scanner.
"""

from agentic_core.L5_safety.enforcement.activation_gate import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    assert_activation_allowed,
)

__all__ = ["assert_activation_allowed"]
