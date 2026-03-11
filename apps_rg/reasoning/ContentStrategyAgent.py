"""CONSOLIDATED: ContentStrategyAgent → RGStrategyExecutor (2026-02-08).

This file is a backward-compatibility shim.
Import the canonical executor directly for new code.
"""

from apps_rg.engines.RGStrategyExecutor import RGStrategyExecutor as ContentStrategyAgent

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

__all__ = ["ContentStrategyAgent"]
