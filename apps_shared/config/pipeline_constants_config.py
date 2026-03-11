"""Shared pipeline constants for apps_rg, apps_lic, and apps_shared.

Single source of truth for module-level constants duplicated across ~25 files.
All apps_* modules MUST import from here instead of defining inline.
"""

MAX_RETRIES: int = 3
DEFAULT_SLEEP: float = 1.0
THRESHOLD: float = 0.95
BUFFER_SIZE: int = 8192
BATCH_SIZE: int = 32
MAX_DEPTH: int = 6
MAX_FILES: int = 1000
DEFAULT_TIMEOUT: int = 300  # 5 minutes

__all__ = [
    "MAX_RETRIES",
    "DEFAULT_SLEEP",
    "THRESHOLD",
    "BUFFER_SIZE",
    "BATCH_SIZE",
    "MAX_DEPTH",
    "MAX_FILES",
    "DEFAULT_TIMEOUT",
]
