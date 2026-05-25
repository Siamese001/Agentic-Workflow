"""Canonical digests for frozen prefix and REGEN_DELTA turns."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _canonical_json(payload: Any) -> str:
    return canonical_json(payload)


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compute_system_prefix_hash(system_text: str) -> str:
    """Hash of concatenated system-authority prefix text."""
    return sha256_hex(system_text.rstrip())


def compute_slot_prefix_digest(slot_snapshot: Mapping[str, str]) -> str:
    """Hash of canonical system+user slot snapshot (ordered keys)."""
    canonical = {k.upper(): v.rstrip() for k, v in sorted(slot_snapshot.items())}
    return sha256_hex(_canonical_json(canonical))


def compute_delta_message_hash(delta_user_content: str) -> str:
    return sha256_hex(delta_user_content.rstrip())
