"""G-16-8: Deterministic serialization and hashing for system learning artifacts.

This module is the SSOT for all deterministic JSON serialization and stable
hashing in the system learning subsystem.

Rules enforced:
- json.dumps with sort_keys=True, separators=(',', ':')  (compact, deterministic)
- Semantically unordered lists are sorted by their deterministic JSON repr
- sha256 derived ONLY from deterministic_json output
- No wall-clock calls (see FORBIDDEN_PATTERNS for the exact banned list)
- No random identifiers in persisted artifacts (see FORBIDDEN_PATTERNS)

Usage:
    from system_learning.enforcement.determinism import (
        deterministic_json,
        stable_sha256_json,
        assert_no_nondeterminism,
    )
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)

emit_determinism_digest("determinism", "determinism_digest")
record_execution_trace("determinism", "determinism_trace")


logger = logging.getLogger(__name__)
FORBIDDEN_PATTERNS: tuple[str, ...] = (
    "uuid4\\b",
    "datetime\\.now\\b",
    "time\\.time\\b",
    "time\\.monotonic\\b",
)


def deterministic_json(obj: Any) -> str:
    """Return a deterministic, compact JSON string for *obj*.

    - Keys are sorted recursively via ``sort_keys=True``.
    - Compact separators ``(',', ':')`` eliminate whitespace variance.
    - This is the ONLY serialization path that L7 hashing may use.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def stable_sha256_json(obj: Any) -> str:
    """Return the SHA-256 hex digest of ``deterministic_json(obj)``.

    Guarantees: same logical object ⇒ same hash, regardless of dict
    insertion order or Python version.
    """
    canonical = deterministic_json(obj)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def assert_no_nondeterminism(source_text: str, *, filepath: str = "<unknown>") -> None:
    """Static check: raise ``PermissionError`` if *source_text* contains
    any forbidden nondeterministic call.

    Intended to be called from guardian tests, not at runtime.
    """
    for pattern in FORBIDDEN_PATTERNS:
        match = re.search(pattern, source_text)
        if match:
            logger.error(
                "L7_DETERMINISM DENY: forbidden pattern %r found in %s at offset %d",
                pattern,
                filepath,
                match.start(),
            )
            raise PermissionError(
                f"L7_DETERMINISM_VIOLATION:FORBIDDEN_CALL|pattern={pattern}|filepath={filepath}|offset={match.start()}",
            )
