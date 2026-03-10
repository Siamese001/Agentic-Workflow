"""Additive determinism helper: canonical_bytes(obj) -> bytes.

Exposes a module-level function used by both production code and replay
harness tests.  Additive artifact for Phase 3 (W5 SOV-DELTA) — no existing
production code changed.

REQ-036 / Phase 3 SOV-DELTA additive helper.
"""

from __future__ import annotations

import json


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def canonical_bytes(obj) -> bytes:
    """Return deterministic canonical bytes for *obj*.

    Uses ``obj.__dict__`` for class/dataclass instances, falls through to
    *obj* itself for plain dict/list/primitive values.  ``sort_keys=True``
    ensures key insertion order does not affect the output.
    """
    data = obj.__dict__ if hasattr(obj, "__dict__") else obj
    return json.dumps(data or obj, sort_keys=True, separators=(",", ":")).encode()
