"""Security utilities for prompt governance."""

from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Lazy imports to avoid circular dependency with detectors
# Use: from agentic_core.prompt_governance.security.utils.injection_scan_util import scan_untrusted_text
# Use: from agentic_core.prompt_governance.security.utils.normalization_util import normalize_and_decode

__all__: list[str] = []
