"""Deterministic replay digest — canonical hash of the run-invariant tuple.

The replay invariant of an agentic run is the four-tuple::

    (route_id, gate_decisions, evidence_packet_ids, final_disposition)

Two replays of the same input MUST produce the same digest. If they don't,
either the run was non-deterministic (a defect) or the invariant tuple was
modified by tampering / drift (also a defect).

The digest is SHA-256 over a canonical JSON encoding. Canonical means:

- Dict keys are sorted ASCII-lexicographically.
- ``gate_decisions`` is normalized to a list of ``[gate_id, verdict]`` pairs
  ordered by ``gate_id`` so caller order doesn't change the digest.
- ``evidence_packet_ids`` is normalized to a sorted, deduplicated list.
- All strings are NFC-normalized to remove accidental Unicode form drift.
- No trailing whitespace; ``separators=(",", ":")`` so insignificant
  whitespace cannot perturb the digest.

W3.1 of plan ``assurance-p1-gates-ab4758``.
"""

from __future__ import annotations

import hashlib
import json
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class ReplayInvariant:
    """The four canonical fields whose tuple identity defines a run."""

    route_id: str
    gate_decisions: tuple[tuple[str, str], ...]
    evidence_packet_ids: tuple[str, ...]
    final_disposition: str
    extra: Mapping[str, Any] = field(default_factory=dict)

    def canonical_dict(self) -> dict[str, Any]:
        """Return the canonical-form dict that gets hashed."""
        return {
            "route_id": _norm_str(self.route_id),
            "gate_decisions": [
                [_norm_str(g), _norm_str(v)] for g, v in sorted(self.gate_decisions, key=lambda gv: gv[0])
            ],
            "evidence_packet_ids": sorted({_norm_str(e) for e in self.evidence_packet_ids}),
            "final_disposition": _norm_str(self.final_disposition),
            "extra": _normalize_mapping(self.extra),
        }

    def canonical_bytes(self) -> bytes:
        """Return canonical JSON bytes used for the digest."""
        return json.dumps(
            self.canonical_dict(),
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")

    def digest(self) -> str:
        """Return SHA-256 hex digest of the canonical bytes."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def compute_digest(
    *,
    route_id: str,
    gate_decisions: Iterable[tuple[str, str]] | Mapping[str, str],
    evidence_packet_ids: Iterable[str],
    final_disposition: str,
    extra: Mapping[str, Any] | None = None,
) -> str:
    """Convenience: build a :class:`ReplayInvariant` and return its digest.

    ``gate_decisions`` may be a list of ``(gate_id, verdict)`` pairs OR a
    dict mapping ``gate_id`` to verdict — both normalize to the same form.
    """
    if isinstance(gate_decisions, Mapping):
        gd: tuple[tuple[str, str], ...] = tuple(gate_decisions.items())
    else:
        gd = tuple((str(g), str(v)) for g, v in gate_decisions)

    inv = ReplayInvariant(
        route_id=str(route_id),
        gate_decisions=gd,
        evidence_packet_ids=tuple(str(e) for e in evidence_packet_ids),
        final_disposition=str(final_disposition),
        extra=extra or {},
    )
    return inv.digest()


def digests_match(a: str, b: str) -> bool:
    """Constant-time-equality digest comparison (paranoia for replay gates)."""
    if len(a) != len(b):
        return False
    diff = 0
    for ca, cb in zip(a, b, strict=True):
        diff |= ord(ca) ^ ord(cb)
    return diff == 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _norm_str(value: Any) -> str:
    """NFC-normalize ``value`` to remove Unicode form drift."""
    return unicodedata.normalize("NFC", str(value))


def _normalize_mapping(m: Mapping[str, Any]) -> dict[str, Any]:
    """Recursively normalize a Mapping for canonical hashing."""
    out: dict[str, Any] = {}
    for k in sorted(m.keys()):
        out[_norm_str(k)] = _normalize_value(m[k])
    return out


def _normalize_value(v: Any) -> Any:
    if isinstance(v, Mapping):
        return _normalize_mapping(v)
    if isinstance(v, (list, tuple)):
        return [_normalize_value(x) for x in v]
    if isinstance(v, str):
        return _norm_str(v)
    if isinstance(v, (int, float, bool)) or v is None:
        return v
    # Fallback: stringify; defensive against unexpected types.
    return _norm_str(v)


__all__ = [
    "ReplayInvariant",
    "compute_digest",
    "digests_match",
]
