"""
Deterministic digest for runtime_state.json.

Produces a stable SHA-256 hex digest that is invariant across runs
whose only differences are wall-clock timestamps.  Reuses the
repo-canonical serializer (agentic_core/utils/canonical_serializer_util.py).

Phase 2 additions:
- Upstream ordering stabilization for UNORDERED scan-result lists.
- Volatile field sentinel for automatic drift detection.
- Digest schema version for contract enforcement.
"""

from __future__ import annotations

import copy
import re
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)
from agentic_core.utils.canonical_serializer_util import canonical_hash

DIGEST_SCHEMA_VERSION: int = 1
EXCLUDE_PATHS: list[str] = [
    "start_time",
    "end_time",
    "events[*].time",
    "completed_agents[*].time",
    "runtime_state_digest_sha256",
    "runtime_state_digest_schema_version",
]
_SORT_SPECS: list[tuple[str, tuple[str, ...]]] = [
    ("compliance_report.violations", ("type", "file", "message")),
    ("location_violations", ("file", "reason")),
    ("location_scan_result.violations", ("file", "reason")),
    ("hygiene_violations", ("type", "file", "message")),
    ("gravity_violations", ("type", "message")),
    ("classification_violations", ("type", "file", "message")),
    ("conversational_violations", ("type", "file", "message")),
    ("compliance_report.drift_violations", ("type", "file", "message")),
]
VOLATILE_FIELD_PATTERNS: list[str] = [
    "time",
    "timestamp",
    "elapsed",
    "uuid",
    "pid",
    "host",
    "nonce",
    "random",
    "seed",
]
_ISO_DATETIME_RE = re.compile("^\\d{4}-\\d{2}-\\d{2}[T ]\\d{2}:\\d{2}:\\d{2}")


def _get_nested(obj: dict[str, Any], dot_path: str) -> Any:
    """Resolve a dot-separated path into *obj*; return None if missing."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_nested", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_nested", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "_get_nested")
    parts = dot_path.split(".")
    cur: Any = obj
    for part in parts:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def _set_nested(obj: dict[str, Any], dot_path: str, value: Any) -> None:
    """Set a value at a dot-separated path inside *obj* (in-place)."""
    parts = dot_path.split(".")
    cur: Any = obj
    for part in parts[:-1]:
        if not isinstance(cur, dict):
            return
        cur = cur.setdefault(part, {})
    if isinstance(cur, dict):
        cur[parts[-1]] = value


def _sort_key(item: Any, keys: tuple[str, ...]) -> tuple[str, ...]:
    """Build a stable sort key from dict *item* using *keys*."""
    if not isinstance(item, dict):
        return (str(item),)
    return tuple(str(item.get(k, "")) for k in keys)


def runtime_state_digest_view(state: dict[str, Any]) -> dict[str, Any]:
    """Return a deep copy of *state* with:
    - excluded fields removed,
    - unordered scan-result lists deterministically sorted,
    - schema version injected.

    - MUST NOT mutate the input.
    - MUST NOT reorder ORDERED lists (events, completed_agents).
    """
    out = copy.deepcopy(state)
    for path in EXCLUDE_PATHS:
        if "[*]" not in path:
            out.pop(path, None)
    for path in EXCLUDE_PATHS:
        if "[*]." in path:
            array_key, field = path.split("[*].", 1)
            arr = out.get(array_key)
            if isinstance(arr, list):
                for item in arr:
                    if isinstance(item, dict):
                        item.pop(field, None)
    for dot_path, sort_keys in _SORT_SPECS:
        lst = _get_nested(out, dot_path)
        if isinstance(lst, list) and lst:
            _set_nested(out, dot_path, sorted(lst, key=lambda item: _sort_key(item, sort_keys)))
    out["_digest_schema_version"] = DIGEST_SCHEMA_VERSION
    return out


def compute_runtime_state_digest(state: dict[str, Any]) -> str:
    """SHA-256 hex digest over the canonical bytes of the digest view.

    Canonicalization is delegated to
    ``agentic_core.utils.canonical_serializer_util.canonical_hash``
    (file: agentic_core/utils/canonical_serializer_util.py:66).
    """
    return canonical_hash(runtime_state_digest_view(state))


def detect_unexcluded_volatile_fields(state: dict[str, Any]) -> list[str]:
    """Traverse *state* and return JSON-path strings for any field that:
    - has a key matching a VOLATILE_FIELD_PATTERNS substring, OR
    - has an ISO-datetime string value,
    AND is NOT already covered by EXCLUDE_PATHS.

    O(n) traversal. Does not mutate input.
    """
    findings: list[str] = []
    _excluded_keys = {
        p.split("[*].")[1] if "[*]." in p else p for p in EXCLUDE_PATHS if "[*]" not in p or "[*]." in p
    }
    _excluded_top = {p for p in EXCLUDE_PATHS if "[*]" not in p}

    def _is_volatile_key(key: str) -> bool:
        key_lower = key.lower()
        return any(pat in key_lower for pat in VOLATILE_FIELD_PATTERNS)

    def _is_volatile_value(val: Any) -> bool:
        return isinstance(val, str) and bool(_ISO_DATETIME_RE.match(val))

    def _walk(obj: Any, path: str) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                child_path = f"{path}.{k}" if path else k
                already_excluded = child_path in _excluded_top or k in _excluded_keys
                if not already_excluded:
                    if _is_volatile_key(k) or _is_volatile_value(v):
                        findings.append(child_path)
                _walk(v, child_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                _walk(item, f"{path}[{i}]")

    _walk(state, "")
    return findings
