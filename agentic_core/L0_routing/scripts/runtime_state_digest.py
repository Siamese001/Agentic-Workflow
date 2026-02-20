"""
Deterministic digest for runtime_state.json.

Produces a stable SHA-256 hex digest that is invariant across runs
whose only differences are wall-clock timestamps.  Reuses the
repo-canonical serializer (agentic_core/utils/canonical_serializer_util.py).
"""

from __future__ import annotations

import copy
from typing import Any

from agentic_core.utils.canonical_serializer_util import canonical_hash

# ── Exclusion paths ─────────────────────────────────────────────────
# JSON-path-like strings identifying non-deterministic fields.
# Top-level scalars are bare names; array-element fields use [*].
EXCLUDE_PATHS: list[str] = [
    "start_time",
    "end_time",
    "events[*].time",
    "completed_agents[*].time",
    "runtime_state_digest_sha256",
]


def runtime_state_digest_view(state: dict[str, Any]) -> dict[str, Any]:
    """Return a deep copy of *state* with excluded fields removed.

    - MUST NOT mutate the input.
    - MUST NOT reorder lists.
    """
    out = copy.deepcopy(state)

    # Remove top-level scalar exclusions
    for path in EXCLUDE_PATHS:
        if "[*]" not in path:
            out.pop(path, None)

    # Remove per-element exclusions  (pattern: "key[*].field")
    for path in EXCLUDE_PATHS:
        if "[*]." in path:
            array_key, field = path.split("[*].", 1)
            arr = out.get(array_key)
            if isinstance(arr, list):
                for item in arr:
                    if isinstance(item, dict):
                        item.pop(field, None)

    return out


def compute_runtime_state_digest(state: dict[str, Any]) -> str:
    """SHA-256 hex digest over the canonical bytes of the digest view.

    Canonicalization is delegated to
    ``agentic_core.utils.canonical_serializer_util.canonical_hash``
    (file: agentic_core/utils/canonical_serializer_util.py:66).
    """
    return canonical_hash(runtime_state_digest_view(state))
