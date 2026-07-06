"""apps_rg HITL reclearance evidence helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping

_HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
_HUMAN_MODIFICATION_KEYS: frozenset[str] = frozenset(
    {"human_modified", "manual_edit", "reentry", "review_override"}
)


@dataclass(frozen=True, slots=True)
class ReClearedHITLPacket:
    """Evidence that a human-modified run re-entered with explicit reclearance."""

    packet_ref: str
    digest: str
    authority_receipt_ref: str
    l5_governance_context_digest: str


def detect_human_modification_flags(value: Any) -> bool:
    """Return True when a payload/artifact tree contains a human-modification flag."""

    if isinstance(value, Mapping):
        for key, inner in value.items():
            if str(key) in _HUMAN_MODIFICATION_KEYS and bool(inner):
                return True
            if detect_human_modification_flags(inner):
                return True
    elif isinstance(value, (list, tuple)):
        return any(detect_human_modification_flags(inner) for inner in value)
    return False


def validate_recleared_hitl_packet(
    packet: ReClearedHITLPacket | Mapping[str, Any] | None,
    *,
    expected_context_digest: str = "",
) -> tuple[bool, tuple[str, ...]]:
    """Validate reclearance evidence without granting runtime authority."""

    if packet is None:
        return False, ("missing_recleared_hitl_packet",)
    if isinstance(packet, Mapping):
        packet = ReClearedHITLPacket(
            packet_ref=str(packet.get("packet_ref") or ""),
            digest=str(packet.get("digest") or ""),
            authority_receipt_ref=str(packet.get("authority_receipt_ref") or ""),
            l5_governance_context_digest=str(
                packet.get("l5_governance_context_digest") or ""
            ),
        )

    reasons: list[str] = []
    if not packet.packet_ref:
        reasons.append("missing_packet_ref")
    if not _HEX64_RE.match(packet.digest):
        reasons.append("malformed_recleared_hitl_digest")
    if not packet.authority_receipt_ref:
        reasons.append("missing_authority_receipt_ref")
    if not _HEX64_RE.match(packet.l5_governance_context_digest):
        reasons.append("malformed_recleared_hitl_context_digest")
    if expected_context_digest and (
        packet.l5_governance_context_digest != expected_context_digest
    ):
        reasons.append("recleared_hitl_context_digest_mismatch")
    return not reasons, tuple(reasons)


__all__ = [
    "ReClearedHITLPacket",
    "detect_human_modification_flags",
    "validate_recleared_hitl_packet",
]
