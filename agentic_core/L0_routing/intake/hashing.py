"""
Stable hashing helpers for raw and normalized payloads.

Hashes are content-addressed; intake uses them for dedupe (E3) and for the
audit/trace fields on the validated_request (E6). We never hash secrets.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


def hash_text(text: str) -> str:
    """SHA-256 hex digest of UTF-8 encoded text."""
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def hash_payload(
    body_text: str | None,
    body_json: Mapping[str, Any] | None,
    attachment_refs: tuple[str, ...] = (),
) -> str:
    """Content-addressed hash combining text body, JSON body, and attachment refs.

    JSON is canonicalized (sorted keys, no whitespace) so logically equivalent
    requests collide on the same hash.
    """
    parts: list[str] = []
    if body_text is not None:
        parts.append("T:" + body_text)
    if body_json is not None:
        try:
            canonical = json.dumps(body_json, sort_keys=True, separators=(",", ":"), default=str)
        except (TypeError, ValueError):
            canonical = repr(body_json)
        parts.append("J:" + canonical)
    if attachment_refs:
        parts.append("A:" + "|".join(sorted(attachment_refs)))
    if not parts:
        return hash_text("")
    return hash_text("\n".join(parts))


__all__ = ["hash_payload", "hash_text"]
