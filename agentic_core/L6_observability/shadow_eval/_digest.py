"""Deterministic digest helpers for L6 shadow-evaluation contracts.

Every L6 receipt/record is required by 06.x doctrine to carry a
``deterministic_digest`` over its canonical content. The digest is a SHA-256
hash over a stable JSON serialization that omits the digest field itself.

This module is the single source of digest semantics for the shadow_eval
package so all builders agree on canonicalization. The digest is the
"content hash" that 06.7 PromotionPacket's ``proposal_content_hash`` and
gauntlet receipts pin to.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
from typing import Any

DIGEST_FIELD = "deterministic_digest"
SEAL_HASH_FIELD = "seal_hash"
CONTENT_HASH_FIELD = "proposal_content_hash"

# Fields that are themselves derived hashes; excluded so a digest covers the
# raw content, not the hash chain.
_DERIVED_HASH_FIELDS = frozenset({DIGEST_FIELD, SEAL_HASH_FIELD, CONTENT_HASH_FIELD, "hmac_sig"})


def _canonicalize(value: Any) -> Any:
    """Recursively convert dataclasses / sets / tuples into JSON-stable forms."""
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return _canonicalize(dataclasses.asdict(value))
    if isinstance(value, dict):
        return {str(k): _canonicalize(value[k]) for k in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_canonicalize(v) for v in value]
    if isinstance(value, (set, frozenset)):
        return [_canonicalize(v) for v in sorted(value, key=repr)]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def canonical_json(payload: Any) -> str:
    """Stable JSON encoding used for digesting and content addressing."""
    return json.dumps(_canonicalize(payload), sort_keys=True, separators=(",", ":"))


def compute_digest(payload: Any, *, exclude: frozenset[str] | None = None) -> str:
    """Compute a SHA-256 hex digest over a payload.

    Excludes derived hash fields by default so the digest reflects raw content.
    """
    excluded = (exclude or frozenset()) | _DERIVED_HASH_FIELDS
    canon = _canonicalize(payload)
    if isinstance(canon, dict):
        canon = {k: v for k, v in canon.items() if k not in excluded}
    encoded = json.dumps(canon, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def stamp_digest(record: Any) -> Any:
    """Attach ``deterministic_digest`` to a dataclass record (returns same object).

    Frozen dataclasses are stamped via ``object.__setattr__``.
    """
    digest = compute_digest(record)
    try:
        object.__setattr__(record, DIGEST_FIELD, digest)
    except (AttributeError, dataclasses.FrozenInstanceError):
        # Last resort for namedtuple-style or fully immutable structures.
        pass
    return record
