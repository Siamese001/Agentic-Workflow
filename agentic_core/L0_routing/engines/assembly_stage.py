"""
Assembly Stage - GAP-03 Implementation
Deterministic composition of governed payloads with stable slot ordering.

This module implements the Assembly Stage that composes system, instructional,
context, and user prompts into a governed payload with deterministic hashing.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


def canonical_bytes(data: dict[str, Any]) -> bytes:
    """
    Convert a dictionary to canonical JSON bytes for deterministic hashing.

    Args:
        data: Dictionary to canonicalize

    Returns:
        Deterministic bytes representation
    """
    return json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


@dataclass(frozen=True)
class GovernedPayload:
    """
    Immutable governed payload with assembly stage slots.

    Slots are ordered S0→D0→I0→C0→U0 for deterministic manifest hashing.
    """

    s0_system: str
    i0_instructional: str
    c0_context: str
    u0_user_prompt: str
    d0_injections: str = ""  # Reserved for future use
    check_ids: tuple[str, ...] = ()
    sanitized: bool = False
    manifest_hash: str = ""

    def __post_init__(self):
        # Compute manifest hash if not provided
        if not self.manifest_hash:
            manifest = {
                "s0_system": self.s0_system,
                "d0_injections": self.d0_injections,
                "i0_instructional": self.i0_instructional,
                "c0_context": self.c0_context,
                "u0_user_prompt": self.u0_user_prompt,
                "check_ids": tuple(sorted(self.check_ids)),
                "sanitized": self.sanitized,
            }
            hash_hex = hashlib.sha256(canonical_bytes(manifest)).hexdigest()
            object.__setattr__(self, "manifest_hash", hash_hex)


class AirlockAssembler:
    """
    Assembly stage for composing governed payloads with deterministic hashing.

    Implements the Assembly Stage (GAP-03) with stable slot composition
    and deterministic manifest hashing.
    """

    @staticmethod
    def assemble(
        *,
        s0_system: str,
        i0_instructional: str,
        c0_context: str,
        u0_user_prompt: str,
        d0_injections: str = "",
    ) -> GovernedPayload:
        """
        Assemble a governed payload from component slots.

        Args:
            s0_system: System prompt slot
            d0_injections: Reserved injection slot (default empty)
            i0_instructional: Instructional prompt slot
            c0_context: Context slot
            u0_user_prompt: User prompt slot

        Returns:
            GovernedPayload with deterministic manifest hash
        """
        # Create payload with slot order S0→D0→I0→C0→U0
        payload = GovernedPayload(
            s0_system=s0_system,
            d0_injections=d0_injections,
            i0_instructional=i0_instructional,
            c0_context=c0_context,
            u0_user_prompt=u0_user_prompt,
        )

        return payload
