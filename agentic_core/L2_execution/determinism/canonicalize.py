"""Additive determinism helper: canonical_bytes(obj) -> bytes.

Exposes a module-level function used by both production code and replay
harness tests.  Additive artifact for Phase 3 (W5 SOV-DELTA) — no existing
production code changed.

REQ-036 / Phase 3 SOV-DELTA additive helper.
"""
from __future__ import annotations
import json
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

def canonical_bytes(obj) -> bytes:
    """Return deterministic canonical bytes for *obj*.

    Uses ``obj.__dict__`` for class/dataclass instances, falls through to
    *obj* itself for plain dict/list/primitive values.  ``sort_keys=True``
    ensures key insertion order does not affect the output.
    """
    data = obj.__dict__ if hasattr(obj, '__dict__') else obj
    return json.dumps(data or obj, sort_keys=True, separators=(',', ':')).encode()
