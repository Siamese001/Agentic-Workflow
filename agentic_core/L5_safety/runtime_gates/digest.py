"""Deterministic digest helpers for runtime gate verdicts.

The doctrine ``GateVerdict`` includes a ``deterministic_digest`` that excludes
wall-clock fields and includes stable packet refs, reason_codes, result,
disposition, thresholds, evidence_refs, and replay_refs (00C.7).

Same helper is used by the orchestrator to build a stable ``GateMeshResult``
digest across multiple verdicts.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping


_STABLE_VERDICT_KEYS: tuple[str, ...] = (
    "gate_id",
    "gate_family",
    "primary_layer",
    "evaluated_packet_ref",
    "request_id",
    "run_id",
    "trace_root",
    "tenant_id",
    "policy_hash",
    "blueprint_hash",
    "replay_key",
    "result",
    "disposition",
    "severity",
    "reason_codes",
    "score",
    "threshold",
    "grader_type",
    "evidence_refs",
    "replay_refs",
    "source_lineage_refs",
    "confidence",
    "abstain_flag",
    "remediation_hint",
    "schema_version",
)


def _canonicalize(value: Any) -> Any:
    """Recursively coerce a value into a stable, comparable JSON shape."""
    if isinstance(value, Mapping):
        return {k: _canonicalize(value[k]) for k in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_canonicalize(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return [_canonicalize(item) for item in sorted(value, key=repr)]
    return value


def verdict_digest(verdict: Mapping[str, Any]) -> str:
    """Compute the deterministic digest for one canonical verdict dict.

    Wall-clock and per-process fields (``created_at_run_offset``,
    ``deterministic_digest`` itself, ``trace_id``, ``span_id``) are excluded.
    """
    payload = {k: _canonicalize(verdict.get(k)) for k in _STABLE_VERDICT_KEYS}
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


def mesh_digest(verdicts: Iterable[Mapping[str, Any]]) -> str:
    """Compute the digest of a sequence of verdicts."""
    digests = [verdict_digest(v) for v in verdicts]
    blob = json.dumps(digests, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()


__all__ = ["verdict_digest", "mesh_digest"]
